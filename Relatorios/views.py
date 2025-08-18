from datetime import datetime
from django.views.generic import TemplateView
from Compras.models import Compra
from Vendas.models import Venda
from Produtos.models import Produto

class RelatorioProdutoView(TemplateView):
    template_name = "relatorioprodutos.html"

    def _parse_date(self, s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data_inicial_str = self.request.GET.get("data_inicial") or ""
        data_final_str = self.request.GET.get("data_final") or ""
        produto_nome = (self.request.GET.get("produto_nome") or "").strip()
        tipo_movimento = self.request.GET.get("tipo_movimento") or "ambos"

        data_inicial = self._parse_date(data_inicial_str)
        data_final = self._parse_date(data_final_str)

        # Lista de produtos para autocomplete
        context["produtos_lista"] = Produto.objects.order_by("NomeProduto").only("id", "NomeProduto")
        context["tipo_movimento"] = tipo_movimento

        movimentos = []
        resumo_por_produto = {}

        # Só filtra se houver algum parâmetro de entrada
        if data_inicial or data_final or produto_nome:

            compra_filters = {}
            venda_filters = {}

            if data_inicial and data_final:
                compra_filters["criados__range"] = (data_inicial, data_final)
                venda_filters["criados__range"] = (data_inicial, data_final)
            if produto_nome:
                compra_filters["produto__NomeProduto__icontains"] = produto_nome
                venda_filters["produto__NomeProduto__icontains"] = produto_nome

            # Função auxiliar para adicionar movimentos
            def add_movimento(qs, tipo, nota_field, contraparte_field):
                for obj in qs:
                    valor_total = (obj.quantidadeProduto or 0) * (obj.precoProduto or 0)
                    movimentos.append({
                        "data": obj.criados,
                        "tipo": tipo,
                        "produto_nome": obj.produto.NomeProduto,
                        "quantidade": obj.quantidadeProduto,
                        "preco_unit": obj.precoProduto,
                        "valor_total": valor_total,
                        "contraparte": getattr(obj, contraparte_field).nomeCliente if tipo=="Venda" else getattr(obj, contraparte_field).nomeFornecedor,
                        "descricao": obj.descricao,
                        "nota": getattr(obj, nota_field),
                        "is_total": False,
                        "show_data": True,
                        "show_tipo": True,
                        "show_nota": True,
                    })

            # Compras
            if tipo_movimento in ["compra", "ambos"]:
                compras_qs = Compra.objects.filter(**compra_filters).select_related("produto", "fornecedor").order_by("identificadorCompra", "id")
                add_movimento(compras_qs, "Compra", "identificadorCompra", "fornecedor")

            # Vendas
            if tipo_movimento in ["venda", "ambos"]:
                vendas_qs = Venda.objects.filter(**venda_filters).select_related("produto", "cliente").order_by("identificadorVenda", "id")
                add_movimento(vendas_qs, "Venda", "identificadorVenda", "cliente")

            # Ordena por nota e id
            movimentos.sort(key=lambda m: (-m["nota"], -m["tipo"], m.get("id", 0)))

            # Ajusta flags para não repetir data/tipo/nota e adiciona linha de total por nota
            final_movimentos = []
            nota_atual = None
            total_nota = 0
            for m in movimentos + [{"nota": None, "tipo": None, "valor_total": 0}]:  # sentinel
                if m["nota"] != nota_atual:
                    if nota_atual is not None:
                        # Linha de total da nota anterior
                        final_movimentos.append({
                            "data": "",
                            "tipo": "",
                            "produto_nome": "TOTAL NOTA",
                            "quantidade": "",
                            "preco_unit": "",
                            "valor_total": total_nota,
                            "contraparte": "",
                            "descricao": "",
                            "nota": "",
                            "is_total": True,
                            "show_data": True,
                            "show_tipo": True,
                            "show_nota": True,
                        })
                    nota_atual = m["nota"]
                    total_nota = 0
                else:
                    m["show_data"] = False
                    m["show_tipo"] = False
                    m["show_nota"] = False
                total_nota += m.get("valor_total", 0)
                if m["nota"] is not None:
                    final_movimentos.append(m)
        else:
            final_movimentos = []  # sem parâmetros, não busca nada

        # Resumo por produto
        for m in final_movimentos:
            if m.get("is_total"):
                continue
            prod = m["produto_nome"]
            if prod not in resumo_por_produto:
                resumo_por_produto[prod] = {
                    "compras_qtd": 0, "compras_valor": 0.0,
                    "vendas_qtd": 0, "vendas_valor": 0.0,
                }
            if m["tipo"] == "Compra":
                resumo_por_produto[prod]["compras_qtd"] += m["quantidade"] or 0
                resumo_por_produto[prod]["compras_valor"] += m["valor_total"] or 0.0
            else:
                resumo_por_produto[prod]["vendas_qtd"] += m["quantidade"] or 0
                resumo_por_produto[prod]["vendas_valor"] += m["valor_total"] or 0.0

        context.update({
            "movimentos": final_movimentos,
            "resumo_por_produto": resumo_por_produto,
            "data_inicial": data_inicial_str,
            "data_final": data_final_str,
            "produto_nome": produto_nome,
        })

        return context

