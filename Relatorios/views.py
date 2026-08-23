from datetime import datetime
from collections import defaultdict
from django.views.generic import TemplateView
from Compras.models import Compra
from Vendas.models import Venda
from Despesas.models import Despesa, CadastroDespesa
from Produtos.models import Produto, CategoriaProduto
from Servicos.models import Servico
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

    def normalizar_nome_produto(self, produto):

        nome = produto.NomeProduto.strip()

        if produto.categoria_id != 1:
            return nome

        partes = nome.split()

        if len(partes) <= 1:
            return nome

        return " ".join(partes[:-1])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        data_inicial_str = self.request.GET.get("data_inicial") or ""
        data_final_str = self.request.GET.get("data_final") or ""
        produtos_selecionados = self.request.GET.getlist("produtos")
        tipo_movimento = self.request.GET.get("tipo_movimento") or "ambos"

        data_inicial = self._parse_date(data_inicial_str)
        data_final = self._parse_date(data_final_str)

        produtos_queryset = Produto.objects.select_related("categoria").order_by("NomeProduto")

        produtos_agrupados = []
        vistos = set()

        for produto in produtos_queryset:
            nome_base = self.normalizar_nome_produto(produto)

            if nome_base not in vistos:
                vistos.add(nome_base)
                produtos_agrupados.append(nome_base)

        context["produtos_lista"] = sorted(produtos_agrupados)
        context["tipo_movimento"] = tipo_movimento

        movimentos = []
        resumo_por_produto = {}

        if data_inicial or data_final or produtos_selecionados:

            compra_filters = {}
            venda_filters = {}

            if data_inicial and data_final:
                compra_filters["criados__range"] = (data_inicial, data_final)
                venda_filters["criados__range"] = (data_inicial, data_final)

            compras_q = Q()
            vendas_q = Q()

            if produtos_selecionados:
                for nome in produtos_selecionados:
                    compras_q |= Q(produto__NomeProduto__istartswith=nome)
                    vendas_q |= Q(produto__NomeProduto__istartswith=nome)

            def add_movimento(qs, tipo, nota_field, contraparte_field):

                for obj in qs:

                    preco_unit = obj.precoProduto if tipo == "Venda" else obj.precoProduto * obj.valorDolarMedio

                    valor_total = (obj.quantidadeProduto or 0) * preco_unit

                    movimentos.append({
                        "data": obj.criados,
                        "tipo": tipo,
                        "produto_nome": self.normalizar_nome_produto(obj.produto),
                        "quantidade": obj.quantidadeProduto,
                        "preco_unit": preco_unit,
                        "valor_total": valor_total,
                        "contraparte": getattr(obj, contraparte_field).nomeCliente if tipo == "Venda" else getattr(obj, contraparte_field).nomeFornecedor,
                        "descricao": obj.descricao,
                        "nota": getattr(obj, nota_field),
                        "is_total": False,
                    })

            if tipo_movimento in ["compra", "ambos"]:
                compras_qs = Compra.objects.filter(**compra_filters).filter(ativo=True).filter(compras_q).select_related("produto", "fornecedor").order_by("-identificadorCompra")
                add_movimento(compras_qs, "Compra", "identificadorCompra", "fornecedor")

            if tipo_movimento in ["venda", "ambos"]:
                vendas_qs = Venda.objects.filter(**venda_filters).filter(ativo=True).filter(vendas_q).select_related("produto", "cliente").order_by("-identificadorVenda")
                add_movimento(vendas_qs, "Venda", "identificadorVenda", "cliente")

        final_movimentos = movimentos

        for m in final_movimentos:

            if m.get("is_total"):
                continue

            prod = m["produto_nome"]

            if prod not in resumo_por_produto:
                resumo_por_produto[prod] = {
                    "compras_qtd": 0,
                    "compras_valor": 0.0,
                    "vendas_qtd": 0,
                    "vendas_valor": 0.0,
                }

            if m["tipo"] == "Compra":
                resumo_por_produto[prod]["compras_qtd"] += m["quantidade"] or 0
                resumo_por_produto[prod]["compras_valor"] += m["valor_total"] or 0.0
            else:
                resumo_por_produto[prod]["vendas_qtd"] += m["quantidade"] or 0
                resumo_por_produto[prod]["vendas_valor"] += m["valor_total"] or 0.0

        # ==========================
        # GRÁFICO
        # ==========================

        grafico = {}

        for m in final_movimentos:

            if m.get("is_total"):
                continue

            if m["tipo"] not in ["Compra", "Venda"]:
                continue

            data_mov = m.get("data")
            if not data_mov:
                continue

            mes = data_mov.strftime("%m/%Y")
            produto = m["produto_nome"]

            chave = produto

            if tipo_movimento == "ambos":
                chave = f"{m['tipo']} - {produto}"

            if chave not in grafico:
                grafico[chave] = {
                    "tipo": m["tipo"],
                    "dados": {}
                }

            grafico[chave]["dados"][mes] = grafico[chave]["dados"].get(mes, 0) + float(m["quantidade"] or 0)

        todos_meses = set()
        for v in grafico.values():
            todos_meses.update(v["dados"].keys())

        labels = sorted(list(todos_meses), key=lambda x: datetime.strptime(x, "%m/%Y"))

        datasets = []

        for produto, info in grafico.items():

            estilo = {
                "label": produto,
                "data": [round(info["dados"].get(mes, 0), 2) for mes in labels],
                "tension": 0.3,
            }

            # 🔥 LINHA POR TIPO
            if info["tipo"] == "Compra":
                estilo["borderDash"] = [6, 6]  # pontilhado
            else:
                estilo["borderDash"] = []      # linha contínua

            datasets.append(estilo)

        context.update({
            "movimentos": final_movimentos,
            "resumo_por_produto": resumo_por_produto,
            "data_inicial": data_inicial_str,
            "data_final": data_final_str,
            "produtos_selecionados": produtos_selecionados,
            "tipo_movimento": tipo_movimento,
            "grafico_labels": labels,
            "grafico_datasets": datasets,
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
        listarVendasTemplate.sort(key=lambda x: x['percentual_lucro'], reverse=True)

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

        # ================= FILTROS =================
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        produto_nome = self.request.GET.get('produto')

        # ================= VENDAS =================
        vendas_qs = Venda.objects.filter(ativo=True)
        if data_inicio:
            vendas_qs = vendas_qs.filter(criados__gte=data_inicio)
        if data_fim:
            vendas_qs = vendas_qs.filter(criados__lte=data_fim)
        if produto_nome:
            vendas_qs = vendas_qs.filter(produto__NomeProduto__icontains=produto_nome)

        # ================= DESPESAS =================
        despesas_qs = Despesa.objects.filter(ativo=True)
        if data_inicio:
            despesas_qs = despesas_qs.filter(modificado__gte=data_inicio)
        if data_fim:
            despesas_qs = despesas_qs.filter(modificado__lte=data_fim)

        # ================= TOTAIS POR MÊS =================
        periodos = (
            vendas_qs.annotate(periodo=TruncMonth('criados'))
            .values('periodo')
            .annotate(
                faturamento=Sum(ExpressionWrapper(F('quantidadeProduto') * F('precoProduto'), output_field=FloatField())),
                lucro_vendas=Sum('lucro')
            )
            .order_by('periodo')
        )

        totais_por_periodo = []
        grafico_labels = []
        grafico_faturamento = []
        grafico_lucro = []

        for p in periodos:
            mes = p['periodo'].month
            ano = p['periodo'].year
            periodo_str = f"{mes:02d}/{ano}"

            faturamento = p['faturamento'] or 0
            lucro_vendas = p['lucro_vendas'] or 0

            # Soma despesas do mesmo mês/ano
            despesas_periodo = despesas_qs.filter(modificado__month=mes, modificado__year=ano)
            valor_despesa_total = sum(d.movimentacao.valorDebito * (d.movimentacao.cotacaoDolar or 1) for d in despesas_periodo)

            # Lucro líquido = lucro de vendas - despesas
            lucro_liquido = lucro_vendas - valor_despesa_total
            margem_percentual = (lucro_liquido * 100 / faturamento) if faturamento > 0 else 0

            totais_por_periodo.append({
                'periodo': periodo_str,
                'faturamento': faturamento,
                'lucro_bruto': lucro_vendas,
                'despesas': valor_despesa_total,
                'lucro_liquido': lucro_liquido,
                'margem_percentual': margem_percentual,
            })

            grafico_labels.append(f"'{periodo_str}'")
            grafico_faturamento.append(faturamento)
            grafico_lucro.append(lucro_liquido)

        # ================= TOTAIS GERAIS =================
        faturamento_total = sum([p['faturamento'] for p in totais_por_periodo])
        lucro_total_bruto = sum([p['lucro_bruto'] for p in totais_por_periodo])
        despesas_total = sum([p['despesas'] for p in totais_por_periodo])
        lucro_total_liquido = lucro_total_bruto - despesas_total
        margem_total = (lucro_total_liquido * 100 / faturamento_total) if faturamento_total else 0

        # ================= PRODUTOS PARA AUTOCOMPLETE =================
        produtos = Produto.objects.filter(ativo=True).order_by('NomeProduto')

        # ================= CONTEXTO =================
        context.update({
            'produtos_lista': produtos,
            'totais_por_periodo': totais_por_periodo,
            'grafico_labels': f"[{','.join(grafico_labels)}]",
            'grafico_faturamento': grafico_faturamento,
            'grafico_lucro': grafico_lucro,
            'faturamento_total': faturamento_total,
            'lucro_total_bruto': lucro_total_bruto,
            'despesas_total': despesas_total,
            'lucro_total_liquido': lucro_total_liquido,
            'margem_total': margem_total,
            'data_inicial': data_inicio,
            'data_final': data_fim,
            'produto_nome': produto_nome,
        })

        return context


class RelatorioServicosTecnicoView(TemplateView):
    template_name = 'relatorioservicostecnico.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        usuario_id = self.request.GET.get("usuario")
        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")
        finalizado = self.request.GET.get("finalizado")

        # ==========================================
        # SERVIÇOS
        # ==========================================

        servicos = Servico.objects.select_related(
            "cliente",
            "usuario"
        )

        # Filtro por técnico
        # IMPORTANTE: filtro somente pelo Servico.usuario
        if usuario_id:
            servicos = servicos.filter(
                usuario_id=usuario_id
            )

        # Filtro por data do SERVIÇO
        if data_inicio:
            servicos = servicos.filter(
                criados__date__gte=parse_date(data_inicio)
            )

        if data_fim:
            servicos = servicos.filter(
                criados__date__lte=parse_date(data_fim)
            )

        # Filtro Finalizado
        if finalizado == "sim":
            servicos = servicos.filter(
                ativo=True
            )

        elif finalizado == "nao":
            servicos = servicos.filter(
                ativo=False
            )

        # Maior identificador primeiro
        servicos = servicos.order_by(
            "-identificador_servico"
        )

        # ==========================================
        # VENDAS DOS SERVIÇOS ENCONTRADOS
        # ==========================================

        identificadores = servicos.values_list(
            "identificador_servico",
            flat=True
        )

        vendas = Venda.objects.select_related(
            "produto",
            "cliente",
            "usuario"
        ).filter(
            identificador_servico__in=identificadores
        )

        # ==========================================
        # AGRUPAR VENDAS POR SERVIÇO
        # ==========================================

        vendas_por_servico = {}

        for venda in vendas:

            venda.total_venda = (
                venda.precoProduto *
                venda.quantidadeProduto
            )

            if venda.identificador_servico not in vendas_por_servico:
                vendas_por_servico[
                    venda.identificador_servico
                ] = []

            vendas_por_servico[
                venda.identificador_servico
            ].append(venda)

        # ==========================================
        # RESUMO DE MATERIAIS
        # ==========================================

        resumo_materiais = {}

        for venda in vendas:

            produto_id = venda.produto_id

            if produto_id not in resumo_materiais:

                resumo_materiais[produto_id] = {
                    "produto": venda.produto.NomeProduto,
                    "quantidade": 0,
                }

            resumo_materiais[produto_id]["quantidade"] += (
                venda.quantidadeProduto
            )

        # Ordenar pelo nome do produto
        resumo_materiais = sorted(
            resumo_materiais.values(),
            key=lambda x: x["produto"].lower()
        )

        # ==========================================
        # RESUMO DE MATERIAIS
        # ==========================================

        resumo_materiais = {}

        for venda in vendas:

            produto_id = venda.produto_id

            if produto_id not in resumo_materiais:
                resumo_materiais[produto_id] = {
                    "produto": venda.produto.NomeProduto,
                    "quantidade": 0,
                }

            resumo_materiais[produto_id]["quantidade"] += (
                venda.quantidadeProduto
            )

        resumo_materiais = sorted(
            resumo_materiais.values(),
            key=lambda x: x["produto"].lower()
        )

        # ==========================================
        # RESUMO DE REPAROS POR TÉCNICO
        # ==========================================

        resumo_reparos = {}

        for venda in vendas:

            if venda.usuario_id:

                usuario_id = venda.usuario_id

                if usuario_id not in resumo_reparos:
                    resumo_reparos[usuario_id] = {
                        "tecnico": venda.usuario.first_name,
                        "quantidade": 0,
                    }

                # IMPORTANTE:
                # Cada registro de Venda conta como 1 reparo.
                # quantidadeProduto NÃO é usado aqui.
                resumo_reparos[usuario_id]["quantidade"] += 1

        resumo_reparos = sorted(
            resumo_reparos.values(),
            key=lambda x: x["tecnico"].lower()
        )


        # ==========================================
        # MONTAR RESULTADO
        # ==========================================

        resultado = []

        for servico in servicos:

            resultado.append({
                "servico": servico,
                "vendas": vendas_por_servico.get(
                    servico.identificador_servico,
                    []
                ),
            })

        # ==========================================
        # CONTEXTO
        # ==========================================

        context["resultado"] = resultado

        context["resumo_materiais"] = resumo_materiais

        context["usuarios"] = User.objects.all().order_by(
            "first_name",
            "username"
        )

        context["usuario_selecionado"] = (
            int(usuario_id)
            if usuario_id
            else None
        )

        context["data_inicio"] = data_inicio
        context["data_fim"] = data_fim
        context["finalizado_selecionado"] = finalizado
        context["resumo_materiais"] = resumo_materiais
        context["resumo_reparos"] = resumo_reparos

        return context
