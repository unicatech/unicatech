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
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from datetime import timedelta
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views.generic import TemplateView


class RelatorioProdutoView(TemplateView):
    template_name = "relatorioprodutos.html"

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def normalizar_nome_produto(produto):
        nome = (
            getattr(produto, "NomeProduto", "") or ""
        ).strip()

        if getattr(produto, "categoria_id", None) != 1:
            return nome

        partes = nome.split()

        if len(partes) > 1:
            return " ".join(partes[:-1])

        return nome

    @staticmethod
    def _get_valor(obj, *nomes, default=None):
        for nome in nomes:
            valor = getattr(obj, nome, None)

            if valor is not None:
                return valor

        return default

    @staticmethod
    def _nome_relacionado(obj, *nomes):
        """
        Retorna um nome legível da relação sem depender de __str__().
        Se não encontrar um campo de nome, usa a chave primária.
        """
        campos_nome = (
            "NomeFornecedor",
            "nome_fornecedor",
            "NomeCliente",
            "nome_cliente",
            "Nome",
            "nome",
            "first_name",
        )

        for nome in nomes:
            relacionado = getattr(obj, nome, None)

            if relacionado is None:
                continue

            for campo in campos_nome:
                valor = getattr(relacionado, campo, None)

                if valor not in (None, ""):
                    return str(valor)

            pk = getattr(relacionado, "pk", None)

            if pk is not None:
                return str(pk)

            # Last resort: protect against a broken __str__().
            try:
                resultado = str(relacionado)
                if isinstance(resultado, str):
                    return resultado
            except (TypeError, ValueError):
                pass

            return ""

        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        data_inicial_texto = request.GET.get(
            "data_inicial", ""
        )
        data_final_texto = request.GET.get(
            "data_final", ""
        )

        data_inicial = self._parse_date(
            data_inicial_texto
        )
        data_final = self._parse_date(
            data_final_texto
        )

        produtos_selecionados = request.GET.getlist(
            "produtos"
        )
        tipo_movimento = request.GET.get(
            "tipo_movimento", "ambos"
        )

        # --------------------------------------------------
        # PRODUTOS DISPONÍVEIS NO FILTRO
        # --------------------------------------------------
        todos_produtos = Produto.objects.all().order_by(
            "NomeProduto"
        )

        produtos_lista = sorted({
            self.normalizar_nome_produto(produto)
            for produto in todos_produtos
            if self.normalizar_nome_produto(produto)
        })

        # --------------------------------------------------
        # FILTROS DE DATA
        # "criados" é DateField; não utilizar __date.
        # --------------------------------------------------
        compra_filters = {"ativo": True}
        venda_filters = {"ativo": True}

        if data_inicial:
            compra_filters["criados__gte"] = data_inicial
            venda_filters["criados__gte"] = data_inicial

        if data_final:
            compra_filters["criados__lte"] = data_final
            venda_filters["criados__lte"] = data_final

        compras = Compra.objects.filter(
            **compra_filters
        ).select_related("produto")

        vendas = Venda.objects.filter(
            **venda_filters
        ).select_related("produto")

        movimentos = []

        resumo_por_produto = defaultdict(
            lambda: {
                "compras_qtd": 0,
                "compras_valor": 0.0,
                "vendas_qtd": 0,
                "vendas_valor": 0.0,
            }
        )

        # --------------------------------------------------
        # ADICIONAR MOVIMENTOS
        # --------------------------------------------------
        def adicionar_movimento(obj, tipo):
            produto_obj = getattr(obj, "produto", None)

            if produto_obj is None:
                return

            nome_produto = (
                self.normalizar_nome_produto(produto_obj)
            )

            # Filtro por produto
            if (
                produtos_selecionados
                and nome_produto not in produtos_selecionados
            ):
                return

            # Filtro por tipo
            if (
                tipo_movimento == "compra"
                and tipo != "Compra"
            ):
                return

            if (
                tipo_movimento == "venda"
                and tipo != "Venda"
            ):
                return

            data_mov = self._get_valor(
                obj, "criados", "data"
            )

            if not data_mov:
                return

            if hasattr(data_mov, "date"):
                data_mov = data_mov.date()

            quantidade = float(
                self._get_valor(
                    obj,
                    "quantidadeProduto",
                    "quantidade",
                    default=0,
                ) or 0
            )

            preco_unit = float(
                self._get_valor(
                    obj,
                    "precoProduto",
                    "preco",
                    default=0,
                ) or 0
            )

            # Converter preço de compra para reais.
            if tipo == "Compra":
                valor_dolar = float(
                    self._get_valor(
                        obj,
                        "valorDolarMedio",
                        default=1,
                    ) or 1
                )

                preco_unit *= valor_dolar

            valor_total = quantidade * preco_unit

            nota = self._get_valor(
                obj,
                "nota",
                "numeroNota",
                "notaFiscal",
                "identificador",
                default="",
            )

            if tipo == "Compra":
                contraparte = self._nome_relacionado(
                    obj,
                    "fornecedor",
                    "Fornecedor",
                )
            else:
                contraparte = self._nome_relacionado(
                    obj,
                    "cliente",
                    "Cliente",
                )

            descricao = self._get_valor(
                obj,
                "descricao",
                "observacao",
                "observacoes",
                default="",
            )

            movimentos.append({
                "data": data_mov,
                "tipo": tipo,
                "produto": nome_produto,
                "quantidade": quantidade,
                "preco_unit": preco_unit,
                "valor_total": valor_total,
                "contraparte": contraparte,
                "descricao": descricao,
                "nota": nota,
                "is_total": False,
            })

            # Resumo por produto
            resumo = resumo_por_produto[nome_produto]

            if tipo == "Compra":
                resumo["compras_qtd"] += quantidade
                resumo["compras_valor"] += valor_total
            else:
                resumo["vendas_qtd"] += quantidade
                resumo["vendas_valor"] += valor_total

        # --------------------------------------------------
        # PROCESSAR DADOS QUANDO HOUVER FILTROS
        # --------------------------------------------------
        tem_filtros = bool(
            data_inicial_texto
            or data_final_texto
            or produtos_selecionados
            or tipo_movimento != "ambos"
        )

        if tem_filtros:
            for compra in compras:
                adicionar_movimento(compra, "Compra")

            for venda in vendas:
                adicionar_movimento(venda, "Venda")

        # --------------------------------------------------
        # ORDENAR MOVIMENTOS
        # --------------------------------------------------
        movimentos.sort(
            key=lambda m: (
                m["data"],
                m["tipo"],
                m["produto"],
            )
        )

        # --------------------------------------------------
        # AGRUPAR VALORES POR DIA
        # --------------------------------------------------
        valores_por_dia = defaultdict(
            lambda: {
                "compras": 0.0,
                "vendas": 0.0,
            }
        )

        for movimento in movimentos:
            dia = movimento["data"]

            if hasattr(dia, "date"):
                dia = dia.date()

            if movimento["tipo"] == "Compra":
                valores_por_dia[dia]["compras"] += (
                    movimento["valor_total"]
                )

            elif movimento["tipo"] == "Venda":
                valores_por_dia[dia]["vendas"] += (
                    movimento["valor_total"]
                )

        # --------------------------------------------------
        # DEFINIR PERÍODO DO GRÁFICO
        # --------------------------------------------------
        datas_movimentos = [
            movimento["data"]
            for movimento in movimentos
        ]

        if data_inicial and data_final:
            inicio = data_inicial
            fim = data_final

        elif data_inicial:
            inicio = data_inicial
            fim = max(
                datas_movimentos + [data_inicial]
            )

        elif data_final:
            inicio = min(
                datas_movimentos + [data_final]
            )
            fim = data_final

        elif datas_movimentos:
            inicio = min(datas_movimentos)
            fim = max(datas_movimentos)

        else:
            inicio = None
            fim = None

        # --------------------------------------------------
        # GRÁFICO DIÁRIO COM ZEROS NOS DIAS SEM MOVIMENTAÇÃO
        # --------------------------------------------------
        grafico_labels = []
        compras_data = []
        vendas_data = []

        if (
            tem_filtros
            and inicio
            and fim
            and inicio <= fim
        ):
            dia_atual = inicio

            while dia_atual <= fim:
                grafico_labels.append(
                    dia_atual.strftime("%d/%m/%Y")
                )

                valores = valores_por_dia[dia_atual]

                compras_data.append(
                    valores["compras"]
                )
                vendas_data.append(
                    valores["vendas"]
                )

                dia_atual += timedelta(days=1)

        grafico_datasets = [
            {
                "label": "Compras",
                "data": compras_data,
                "borderDash": [5, 5],
                "fill": False,
                "tension": 0,
            },
            {
                "label": "Vendas",
                "data": vendas_data,
                "borderDash": [],
                "fill": False,
                "tension": 0,
            },
        ]

        # --------------------------------------------------
        # CONTEXTO DO TEMPLATE
        # --------------------------------------------------
        context.update({
            "movimentos": movimentos,
            "resumo_por_produto": dict(
                resumo_por_produto
            ),
            "produtos_lista": produtos_lista,
            "produtos_selecionados": (
                produtos_selecionados
            ),
            "data_inicial": data_inicial_texto,
            "data_final": data_final_texto,
            "tipo_movimento": tipo_movimento,
            "grafico_labels": grafico_labels,
            "grafico_datasets": grafico_datasets,
        })

        return context




class RelatorioRecebimentosContasView(TemplateView):
    template_name = 'relatoriocontas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ==========================================================
        # FILTROS
        # ==========================================================
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        conta_id = self.request.GET.get('conta')

        hoje = timezone.localdate()

        # ==========================================================
        # PERÍODO PADRÃO
        # Se nenhuma data foi informada, utiliza os últimos 6 meses
        # ==========================================================
        if not data_inicio and not data_fim:
            data_inicio_parsed = hoje - relativedelta(months=6)
            data_fim_parsed = hoje

            data_inicio = data_inicio_parsed
            data_fim = data_fim_parsed

        else:
            data_inicio_parsed = parse_date(data_inicio) if data_inicio else None
            data_fim_parsed = parse_date(data_fim) if data_fim else None

            # Se somente a data inicial foi informada
            if data_inicio_parsed and not data_fim_parsed:
                data_fim_parsed = hoje
                data_fim = data_fim_parsed

            # Se somente a data final foi informada
            elif data_fim_parsed and not data_inicio_parsed:
                data_inicio_parsed = data_fim_parsed - relativedelta(months=6)
                data_inicio = data_inicio_parsed

        # ==========================================================
        # QUERY BASE
        # ==========================================================
        movimentacoes = MovimentacaoConta.objects.filter(
            identificadorVenda__gt=0,
            valorDebito=0,
            valorCredito__gt=0,
            ativo=True
        ).select_related(
            'contaCredito'
        )

        # ==========================================================
        # FILTRO DE DATA
        # ==========================================================
        if data_inicio_parsed:
            movimentacoes = movimentacoes.filter(
                criados__gte=data_inicio_parsed
            )

        if data_fim_parsed:
            # Inclui TODO o dia informado em data_fim.
            # Em vez de <= 00:00:00, usamos < dia seguinte.
            data_fim_exclusiva = data_fim_parsed + timedelta(days=1)

            movimentacoes = movimentacoes.filter(
                criados__lt=data_fim_exclusiva
            )

        # ==========================================================
        # FILTRO POR CONTA
        # ==========================================================
        conta_selecionada = None

        if conta_id and conta_id.isdigit():
            conta_selecionada = int(conta_id)

            movimentacoes = movimentacoes.filter(
                contaCredito_id=conta_selecionada
            )

        movimentacoes = movimentacoes.order_by(
            '-identificadorVenda',
            '-criados'
        )

        # ==========================================================
        # TOTAL DA VENDA
        # ==========================================================
        totais_por_venda = movimentacoes.values(
            'identificadorVenda'
        ).annotate(
            total_credito=Sum('valorCredito')
        )

        totais_dict = {
            item['identificadorVenda']: item['total_credito']
            for item in totais_por_venda
        }

        # ==========================================================
        # LISTA DE MOVIMENTAÇÕES
        # ==========================================================
        lista_final = []

        for mov in movimentacoes:

            conta_nome = (
                mov.contaCredito.nomeConta
                if mov.contaCredito
                else 'N/A'
            )

            lista_final.append({
                'id': mov.id,
                'data_criacao': mov.criados,
                'identificadorVenda': mov.identificadorVenda,
                'valorCredito': mov.valorCredito,
                'total_credito_venda': totais_dict.get(
                    mov.identificadorVenda,
                    mov.valorCredito
                ),
                'contaCredito_nome': conta_nome,
                'descricao': mov.descricao,
            })

        # ==========================================================
        # TODAS AS CONTAS
        # ==========================================================
        contas = Conta.objects.all().order_by('nomeConta')

        # ==========================================================
        # TOTAL RECEBIDO POR CONTA
        # ==========================================================
        totais_contas_query = movimentacoes.values(
            'contaCredito_id',
            'contaCredito__nomeConta'
        ).annotate(
            total_recebido=Sum('valorCredito')
        ).order_by(
            'contaCredito__nomeConta'
        )

        totais_contas = []

        total_geral = 0

        for item in totais_contas_query:

            total = item['total_recebido'] or 0

            totais_contas.append({
                'id': item['contaCredito_id'],
                'nome': item['contaCredito__nomeConta'],
                'total': total,
            })

            total_geral += total

        # ==========================================================
        # DADOS DOS GRÁFICOS
        #
        # Cada conta terá um gráfico mostrando os recebimentos
        # agrupados por mês.
        # ==========================================================

        graficos_contas = []

        for conta in totais_contas:

            conta_id_grafico = conta['id']

            movimentos_conta = movimentacoes.filter(
                contaCredito_id=conta_id_grafico
            )

            # Agrupamento por mês
            valores_por_mes = {}

            for mov in movimentos_conta:

                if not mov.criados:
                    continue

                mes = mov.criados.strftime('%Y-%m')

                if mes not in valores_por_mes:
                    valores_por_mes[mes] = 0

                valores_por_mes[mes] += float(
                    mov.valorCredito or 0
                )

            # ------------------------------------------------------
            # Gera todos os meses do período
            # Mesmo que não tenha recebido nada naquele mês.
            # ------------------------------------------------------

            meses = []

            if data_inicio_parsed and data_fim_parsed:

                primeiro_mes = data_inicio_parsed.replace(day=1)
                ultimo_mes = data_fim_parsed.replace(day=1)

                mes_atual = primeiro_mes

                while mes_atual <= ultimo_mes:

                    chave = mes_atual.strftime('%Y-%m')

                    # Nome apresentado no gráfico
                    nome_mes = mes_atual.strftime('%m/%Y')

                    meses.append({
                        'chave': chave,
                        'nome': nome_mes,
                        'valor': round(
                            valores_por_mes.get(chave, 0),
                            2
                        )
                    })

                    mes_atual = mes_atual + relativedelta(
                        months=1
                    )

            graficos_contas.append({
                'id': conta_id_grafico,
                'nome': conta['nome'],
                'meses': meses,
                'total': float(conta['total'] or 0),
            })

        # ==========================================================
        # CONTEXTO
        # ==========================================================

        context.update({

            # Movimentações
            'movimentacoes': lista_final,

            # Contas do select
            'contas': contas,

            # Período
            'data_inicio': data_inicio_parsed,
            'data_fim': data_fim_parsed,

            # Conta selecionada
            'conta_selecionada': conta_selecionada,

            # Resumo por conta
            'totais_contas': totais_contas,

            # Total geral
            'total_geral': total_geral,

            # Dados dos gráficos
            'graficos_contas': graficos_contas,
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

class RelatorioLucroVendasView(TemplateView):

    template_name = 'relatoriolucrovendas.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")

        # ==========================================
        # VENDAS
        # ==========================================

        vendas = Venda.objects.select_related(
            "produto",
            "cliente",
            "usuario"
        ).filter(
            ativo=True
        )

        # ==========================================
        # FILTRO POR DATA
        # ==========================================

        if data_inicio or data_fim:

            # Se o usuário informou alguma data,
            # não aplicar a restrição dos 3 meses

            if data_inicio:
                vendas = vendas.filter(
                    modificado__date__gte=parse_date(data_inicio)
                )

            if data_fim:
                vendas = vendas.filter(
                    modificado__date__lte=parse_date(data_fim)
                )

        else:

            # Nenhuma data informada:
            # mostrar somente os últimos 3 meses

            data_limite = now() - timedelta(days=90)

            vendas = vendas.filter(
                modificado__gte=data_limite
            )

        # ==========================================
        # ORDENAR
        # ==========================================

        vendas = vendas.order_by(
            "-identificadorVenda",
            "id"
        )

        # ==========================================
        # AGRUPAR POR VENDA
        # ==========================================

        vendas_por_identificador = {}

        for venda in vendas:

            # ======================================
            # VALOR DO PRODUTO
            # ======================================

            venda.valor_produto = (
                venda.precoProduto *
                venda.quantidadeProduto
            )

            # ======================================
            # LUCRO DO PRODUTO
            # ======================================

            venda.lucro_produto = (
                venda.lucro
            )

            # ======================================
            # CRIAR VENDA
            # ======================================

            if venda.identificadorVenda not in vendas_por_identificador:

                vendas_por_identificador[
                    venda.identificadorVenda
                ] = {
                    "identificador": venda.identificadorVenda,

                    "identificador_servico": (
                        venda.identificador_servico
                    ),

                    "data_modificado": venda.modificado,

                    "produtos": [],

                    "valor_total": 0,

                    "lucro_total": 0,
                }

            venda_atual = vendas_por_identificador[
                venda.identificadorVenda
            ]

            # ======================================
            # ADICIONAR PRODUTO
            # ======================================

            venda_atual["produtos"].append(venda)

            # ======================================
            # SOMAR VALOR DA VENDA
            # ======================================

            venda_atual["valor_total"] += (
                venda.valor_produto
            )

            # ======================================
            # SOMAR LUCRO DA VENDA
            # ======================================

            venda_atual["lucro_total"] += (
                venda.lucro_produto
            )

        # ==========================================
        # TRANSFORMAR DICIONÁRIO EM LISTA
        # ==========================================

        resultado = list(
            vendas_por_identificador.values()
        )

        # ==========================================
        # TOTAIS GERAIS
        # ==========================================

        valor_total_geral = sum(
            venda["valor_total"]
            for venda in resultado
        )

        lucro_total_geral = sum(
            venda["lucro_total"]
            for venda in resultado
        )

        # ==========================================
        # CONTEXTO
        # ==========================================

        context["resultado"] = resultado

        context["valor_total_geral"] = (
            valor_total_geral
        )

        context["lucro_total_geral"] = (
            lucro_total_geral
        )

        context["data_inicio"] = data_inicio
        context["data_fim"] = data_fim

        return context