from datetime import datetime
from django.views.generic import TemplateView
from Compras.models import Compra
from Vendas.models import Venda
from Despesas.models import Despesa, CadastroDespesa
from Produtos.models import Produto, CategoriaProduto
from django.db.models import F, Sum, Min, Count, FloatField, Q
from django.db.models.functions import Lower
from django.utils.dateparse import parse_date
from Contas.models import RecebimentoCartao, MovimentacaoConta, Conta
from django.db.models import (
    Sum,
    F,
    FloatField,
    ExpressionWrapper,
    Case,
    When,
    Value
)
from django.db.models.functions import TruncMonth, TruncYear
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from core.models import Alertas
from datetime import datetime, time

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
                compras_qs = Compra.objects.filter(**compra_filters).filter(ativo=True).select_related("produto", "fornecedor").order_by("identificadorCompra", "id")
                add_movimento(compras_qs, "Compra", "identificadorCompra", "fornecedor")

            # Vendas
            if tipo_movimento in ["venda", "ambos"]:
                vendas_qs = Venda.objects.filter(**venda_filters).filter(ativo=True).select_related("produto", "cliente").order_by("identificadorVenda", "id")
                add_movimento(vendas_qs, "Venda", "identificadorVenda", "cliente")

            # Ordena por nota e id
            movimentos.sort(key=lambda m: (-m["nota"], m["tipo"], m.get("id", 0)))

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

class RelatorioRecebimentoCartaoView(TemplateView):
    template_name = "relatoriocartoes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros recebidos
        data_inicial = self.request.GET.get("data_inicial")
        data_final = self.request.GET.get("data_final")
        bandeira = self.request.GET.get("bandeira")

        # Query base
        recebimentos = RecebimentoCartao.objects.all().order_by("-criados").filter(ativo=True)

        # Filtro por datas
        if data_inicial:
            recebimentos = recebimentos.filter(criados__gte=parse_date(data_inicial))
        if data_final:
            recebimentos = recebimentos.filter(criados__lte=parse_date(data_final))

        # Filtro por bandeira
        if bandeira:
            recebimentos = recebimentos.filter(bandeira__icontains=bandeira)

        # Lista de bandeiras únicas (para o datalist)
        bandeiras_lista = (
            RecebimentoCartao.objects.values_list("bandeira", flat=True)
            .distinct()
            .order_by("bandeira")
        )

        # Resumo agrupado
        resumo = (
            recebimentos.values("bandeira")
            .annotate(
                total_valor=Sum("valor"),
                total_liquido=Sum("valor_liquido")
            )
            .order_by("bandeira")
        )

        context.update({
            "recebimentos": recebimentos,
            "data_inicial": data_inicial or "",
            "data_final": data_final or "",
            "bandeira": bandeira or "",
            "resumo": resumo,
            "bandeiras_lista": bandeiras_lista,
            "total_bruto": sum(r.valor for r in recebimentos),
            "total_liquido": sum(r.valor_liquido for r in recebimentos),
        })

        return context

class RelatorioRecebimentosContasView(TemplateView):
    template_name = 'relatoriocontas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ====== FILTROS ======
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        conta_id = self.request.GET.get('conta')

        # ====== QUERY BASE ======
        movimentacoes = MovimentacaoConta.objects.filter(
            identificadorVenda__gt=0,
            valorDebito=0,
            valorCredito__gt=0,
            ativo=True
        ).select_related('contaCredito').order_by('-identificadorVenda','-criados')

        # Filtro por data
        if data_inicio:
            data_inicio_parsed = parse_date(data_inicio)
            if data_inicio_parsed:
                movimentacoes = movimentacoes.filter(criados__gte=data_inicio_parsed)

        if data_fim:
            data_fim_parsed = parse_date(data_fim)
            if data_fim_parsed:
                movimentacoes = movimentacoes.filter(criados__lte=data_fim_parsed)

        # Filtro por conta
        if conta_id and conta_id.isdigit():
            movimentacoes = movimentacoes.filter(contaCredito_id=int(conta_id))

        # ====== AGRUPAMENTO PARA SOMAR VALORES POR identificadorVenda ======
        # Calcula o total de cada venda
        totais_por_venda = movimentacoes.values('identificadorVenda').annotate(
            total_credito=Sum('valorCredito')
        )
        totais_dict = {item['identificadorVenda']: item['total_credito'] for item in totais_por_venda}

        # Prepara a lista final de registros, mantendo todos os movimentos
        lista_final = []
        for mov in movimentacoes:
            conta_nome = mov.contaCredito.nomeConta if mov.contaCredito else 'N/A'
            lista_final.append({
                'id': mov.id,
                'data_criacao': mov.criados,
                'identificadorVenda': mov.identificadorVenda,
                'valorCredito': mov.valorCredito,
                'total_credito_venda': totais_dict.get(mov.identificadorVenda, mov.valorCredito),
                'contaCredito_nome': conta_nome,
                'descricao': mov.descricao,
            })

        # Todas as contas para o select
        contas = Conta.objects.all().order_by('nomeConta')

        # Atualiza o contexto
        context.update({
            'movimentacoes': lista_final,
            'contas': contas,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'conta_selecionada': int(conta_id) if conta_id and conta_id.isdigit() else None,
        })

        return context

    def get_template_names(self):
        if self.request.GET.get("funcao") == "modal":
            return ["detalhesvendamodal.html"]
        return [self.template_name]


class RelatorioRecebimentoProdutosView(TemplateView):
    template_name = 'relatoriorecebimentoprodutos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtros
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        categoria_id = self.request.GET.get('categoria_id')

        vendas = Venda.objects.filter(ativo=True).select_related('produto', 'produto__categoria')

        # Filtrar por datas
        if data_inicio and data_fim:
            try:
                dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
                vendas = vendas.filter(criados__range=[dt_inicio, dt_fim])
            except:
                pass

        # Filtrar por categoria
        if categoria_id:
            vendas = vendas.filter(produto__categoria_id=categoria_id)

        total_vendas = 0
        total_lucro = 0

        agrupados = {}

        for venda in vendas:
            nome_produto = venda.produto.NomeProduto.strip()
            categoria_nome = venda.produto.categoria.categoria

            # Agrupamento especial para iPhone (remover última palavra = cor)
            if categoria_nome.lower() == 'iphone':
                palavras = nome_produto.split()
                if len(palavras) > 1:
                    modelo_base = " ".join(palavras[:-1])
                else:
                    modelo_base = palavras[0]
            else:
                modelo_base = nome_produto

            chave = modelo_base.lower()

            if chave not in agrupados:
                agrupados[chave] = {
                    'produto': modelo_base,
                    'valor_venda': 0,
                    'lucro': 0
                }

            valor_venda = venda.quantidadeProduto * venda.precoProduto
            agrupados[chave]['valor_venda'] += valor_venda
            agrupados[chave]['lucro'] += venda.lucro

            total_vendas += valor_venda
            total_lucro += venda.lucro

        # Calcular percentuais
        listarVendasTemplate = []
        for item in agrupados.values():
            listarVendasTemplate.append({
                'produto': item['produto'],
                'valor_venda': item['valor_venda'],
                'lucro': item['lucro'],
                'percentual_venda': (item['valor_venda'] / total_vendas * 100) if total_vendas else 0,
                'percentual_lucro': (item['lucro'] / total_lucro * 100) if total_lucro else 0
            })

        context['listarVendasTemplate'] = listarVendasTemplate
        context['total_vendas'] = total_vendas
        context['total_lucro'] = total_lucro
        context['categorias'] = CategoriaProduto.objects.all()
        context['request'] = self.request

        return context


class RelatorioEventosView(TemplateView):
    template_name = 'relatorioeventos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        alertas = Alertas.objects.all()

        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        usuario_id = self.request.GET.get('usuario')

        # ===== FILTRO POR DATA =====
        if data_inicio:
            alertas = alertas.filter(
                criados__gte=datetime.strptime(data_inicio, '%Y-%m-%d')
            )

        if data_fim:
            alertas = alertas.filter(
                criados__lte=datetime.combine(
                    datetime.strptime(data_fim, '%Y-%m-%d'),
                    time.max
                )
            )

        # ===== FILTRO POR USUÁRIO =====
        if usuario_id:
            alertas = alertas.filter(usuario_id=usuario_id)

        alertas = alertas.order_by('-criados')

        context.update({
            'alertas': alertas,
            'usuarios': User.objects.all().order_by('first_name'),
            'total_alertas': alertas.count(),
        })

        return context

class RelatorioFaturamentoeLucroView(TemplateView):
    template_name = "relatorio_faturamento_lucro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        produto_nome = self.request.GET.get('produto')

        # Filtra vendas
        vendas_qs = Venda.objects.filter(ativo=True)
        if data_inicio:
            vendas_qs = vendas_qs.filter(criados__gte=data_inicio)
        if data_fim:
            vendas_qs = vendas_qs.filter(criados__lte=data_fim)
        if produto_nome:
            vendas_qs = vendas_qs.filter(produto__NomeProduto__icontains=produto_nome)

        # ================= PRODUTOS PARA AUTOCOMPLETE =================
        produtos = Produto.objects.filter(ativo=True).order_by('NomeProduto')

        # ================= DADOS DETALHADOS =================
        resultados = (
            vendas_qs.values(
                'produto__SKU',
                'produto__NomeProduto',
                'produto__categoria__categoria'
            )
            .annotate(
                faturamento=Sum(ExpressionWrapper(F('quantidadeProduto') * F('precoProduto'), output_field=FloatField())),
                lucro_total=Sum('lucro')
            )
        )

        # ================= DESPESAS NO PERÍODO =================
        despesas_qs = Despesa.objects.filter(
            movimentacao__criados__gte=data_inicio if data_inicio else datetime(1900,1,1),
            movimentacao__criados__lte=data_fim if data_fim else datetime.today()
        )

        total_despesas = despesas_qs.aggregate(
            total=Sum('despesa__valor')
        )['total'] or 0

        # ================= LUCRO LÍQUIDO =================
        for r in resultados:
            r['lucro_liquido'] = (r['lucro_total'] or 0)  # Despesas não subtraídas por produto individualmente
            r['margem_percentual'] = (r['lucro_liquido'] * 100 / r['faturamento']) if r['faturamento'] > 0 else 0

        # ================= TOTAIS GERAIS =================
        faturamento_total = sum([r['faturamento'] or 0 for r in resultados])
        lucro_total = sum([r['lucro_liquido'] or 0 for r in resultados]) - total_despesas
        margem_total = (lucro_total * 100 / faturamento_total) if faturamento_total > 0 else 0

        # ================= TOTAIS POR MÊS =================
        periodos = (
            vendas_qs.annotate(periodo=TruncMonth('criados'))
            .values('periodo')
            .annotate(
                faturamento=Sum(ExpressionWrapper(F('quantidadeProduto') * F('precoProduto'), output_field=FloatField())),
                lucro=Sum('lucro')
            )
            .order_by('periodo')
        )

        totais_por_periodo = []
        grafico_labels = []
        grafico_faturamento = []
        grafico_lucro = []

        for p in periodos:
            m = p['periodo'].month
            a = p['periodo'].year
            periodo_str = f"{m:02d}/{a}"
            fatur = p['faturamento'] or 0
            lucro = (p['lucro'] or 0)

            # Subtraímos proporcionalmente as despesas do mês (simplificação: dividir total_despesas igualmente)
            # Se quiser precisão real, precisaremos vincular cada despesa ao mês exato
            lucro_liquido = lucro - (total_despesas / len(periodos)) if len(periodos) > 0 else lucro

            margem = (lucro_liquido * 100 / fatur) if fatur > 0 else 0

            totais_por_periodo.append({
                'periodo': periodo_str,
                'faturamento': fatur,
                'lucro': lucro_liquido,
                'margem_percentual': margem,
            })

            grafico_labels.append(f"'{periodo_str}'")
            grafico_faturamento.append(fatur)
            grafico_lucro.append(lucro_liquido)

        # ================= CONTEXTO =================
        context.update({
            'resultados': resultados,
            'produtos_lista': produtos,
            'faturamento_total': faturamento_total,
            'lucro_total_geral': lucro_total,
            'margem_total': margem_total,
            'totais_por_periodo': totais_por_periodo,
            'grafico_labels': f"[{','.join(grafico_labels)}]",
            'grafico_faturamento': grafico_faturamento,
            'grafico_lucro': grafico_lucro,
            'data_inicial': data_inicio,
            'data_final': data_fim,
            'produto_nome': produto_nome,
            'total_despesas': total_despesas,
        })

        return context