import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Calculadora de Lucro - Moto & Carro", page_icon="🛵", layout="centered")

# Inicializa o histórico de corridas na sessão do usuário
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Estilo CSS customizado
st.markdown("""
<style>
    .app-title {
        color: #2b3d52;
        font-weight: 700;
        border-bottom: 2px solid #dee2e6;
        padding-bottom: 10px;
        margin-bottom: 15px;
        text-align: center;
    }
    .result-box {
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        font-weight: bold;
        text-align: center;
    }
    .status-ok { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-warn { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .status-danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='app-title'>🛵🚗 Calculadora de Lucro Real</h2>", unsafe_allow_html=True)

# Abas para organizar o App
aba_calc, aba_historico, aba_loja = st.tabs(["📊 Calcular Rota", "📅 Meu Dia (Histórico)", "🛒 Equipamentos"])

# ==========================================
# ABA 1: CALCULADORA DE ROTA
# ==========================================
with aba_calc:
    # Escolha principal: Moto ou Carro
    tipo_veiculo = st.radio("Selecione o seu veículo:", ["🏍️ Moto", "🚗 Carro"], horizontal=True)

    if tipo_veiculo == "🏍️ Moto":
        perfis = {
            "Moto 125cc / 150cc / 160cc": {"consumo": 36.0, "manut": 0.12},
            "Moto 250cc / 300cc": {"consumo": 28.0, "manut": 0.18},
            "Moto Elétrica": {"consumo": 50.0, "manut": 0.10}
        }
        meta_minima_km = 0.80     # R$/km líquido mínimo
        meta_boa_km = 1.20        # R$/km líquido excelente
        meta_minima_hora = 20.00  # R$/hora líquido mínimo
        meta_boa_hora = 28.00     # R$/hora líquido excelente
        sugestao_dist = 6.0
        sugestao_valor = 12.0
        sugestao_tempo = 18
    else:
        perfis = {
            "Carro 1.0 Aspirado": {"consumo": 11.5, "manut": 0.25},
            "Carro 1.0 Turbo": {"consumo": 10.5, "manut": 0.30},
            "Carro 1.4 / 1.5": {"consumo": 9.5, "manut": 0.32},
            "Carro 1.6 / 1.8": {"consumo": 8.5, "manut": 0.38},
            "Carro 2.0 ou SUV": {"consumo": 7.0, "manut": 0.48},
            "Carro Híbrido": {"consumo": 17.5, "manut": 0.32}
        }
        meta_minima_km = 1.30     # R$/km líquido mínimo
        meta_boa_km = 1.75        # R$/km líquido excelente
        meta_minima_hora = 25.00  # R$/hora líquido mínimo
        meta_boa_hora = 35.00     # R$/hora líquido excelente
        sugestao_dist = 10.0
        sugestao_valor = 24.0
        sugestao_tempo = 25

    opcoes_combustivel = {
        'Gasolina': 5.89,
        'Etanol': 3.99,
        'GNV': 4.75,
        'Diesel': 6.15,
        'Outro (Definir)': 0.0
    }

    c_top1, c_top2 = st.columns(2)
    with c_top1:
        modelo_selecionado = st.selectbox("Modelo / Motorização:", list(perfis.keys()))
    with c_top2:
        combustivel_selecionado = st.selectbox("Combustível:", list(opcoes_combustivel.keys()))

    # Ajuste automático de consumo (Etanol rende ~30% menos)
    perfil = perfis[modelo_selecionado]
    consumo_sugerido = perfil["consumo"] * 0.70 if combustivel_selecionado == "Etanol" else perfil["consumo"]
    preco_padrao = opcoes_combustivel[combustivel_selecionado]

    col1, col2 = st.columns(2)
    with col1:
        preco_comb = st.number_input("Preço Litro/m³ (R$):", min_value=0.0, value=float(preco_padrao) if preco_padrao > 0 else 5.00, step=0.10, format="%.2f")
        distancia = st.number_input("Distância Total + Busca (km):", min_value=0.0, value=sugestao_dist, step=0.5, format="%.1f")
        tempo_min = st.number_input("Tempo Total Estimado (minutos):", min_value=1, value=sugestao_tempo, step=1)

    with col2:
        consumo = st.number_input("Consumo Médio (km/L ou m³):", min_value=0.0, value=round(consumo_sugerido, 1), step=0.5, format="%.1f")
        valor_corrida = st.number_input("Valor da Corrida/Entrega (R$):", min_value=0.0, value=sugestao_valor, step=0.5, format="%.2f")

    custo_km_manut = st.slider(
        "Desgaste/Manutenção por km (pneu, óleo, relação/revisão, depreciação - R$/km):",
        min_value=0.05,
        max_value=0.80,
        value=float(perfil["manut"]),
        step=0.02
    )

    if st.button("Analisar Viabilidade", type="primary", use_container_width=True):
        if consumo <= 0 or preco_comb <= 0 or distancia <= 0 or valor_corrida <= 0 or tempo_min <= 0:
            st.markdown("<div class='result-box status-danger'>⚠️ Preencha todos os campos com valores maiores que zero!</div>", unsafe_allow_html=True)
        else:
            custo_combustivel = (distancia / consumo) * preco_comb
            custo_manutencao = distancia * custo_km_manut
            custo_total = custo_combustivel + custo_manutencao
            saldo_liquido = valor_corrida - custo_total
            margem = (saldo_liquido / valor_corrida) * 100
            
            ganho_por_km = saldo_liquido / distancia
            bruto_por_km = valor_corrida / distancia
            ganho_por_hora = (saldo_liquido / tempo_min) * 60
            bruto_por_hora = (valor_corrida / tempo_min) * 60

            # Análise combinada: Distância (KM) + Trânsito (HORA)
            if saldo_liquido <= 0:
                classe_status = "status-danger"
                status_txt = "🚨 PREJUÍZO REAL! Você está pagando do próprio bolso para fazer essa rota."
            elif ganho_por_km < meta_minima_km and ganho_por_hora < meta_minima_hora:
                classe_status = "status-danger"
                status_txt = f"❌ NÃO COMPENSA! Paga mal por km (R$ {ganho_por_km:.2f}/km) e prende no trânsito (R$ {ganho_por_hora:.2f}/h)."
            elif ganho_por_km < meta_minima_km:
                classe_status = "status-danger"
                status_txt = f"❌ DESGASTE ALTO! Apesar do tempo curto, paga apenas R$ {ganho_por_km:.2f}/km líquido (mínimo: R$ {meta_minima_km:.2f}/km)."
            elif ganho_por_hora < meta_minima_hora:
                classe_status = "status-warn"
                status_txt = f"⚠️ ARMADILHA DE TRÂNSITO! Paga bem por km (R$ {ganho_por_km:.2f}/km), mas o trânsito derruba seu ganho para R$ {ganho_por_hora:.2f}/hora."
            elif ganho_por_km >= meta_boa_km and ganho_por_hora >= meta_boa_hora:
                classe_status = "status-ok"
                status_txt = f"✅ EXCELENTE! Paga R$ {ganho_por_km:.2f}/km e R$ {ganho_por_hora:.2f}/hora líquidos. Aceite na hora!"
            else:
                classe_status = "status-warn"
                status_txt = f"👍 RAZOÁVEL (R$ {ganho_por_km:.2f}/km | R$ {ganho_por_hora:.2f}/h). Boa para manter o giro ou ir para área melhor."

            cor_lucro = '#28a745' if (ganho_por_km >= meta_minima_km and ganho_por_hora >= meta_minima_hora) else '#dc3545'

            html_resultado = f"""
            <div style='margin-top: 15px; border-top: 1px solid #dee2e6; padding-top: 15px;'>
                <table style='width: 100%; border-collapse: collapse; font-size: 15px;'>
                    <tr><td style='padding: 5px 0;'>⛽ Combustível:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_combustivel:.2f}</td></tr>
                    <tr><td style='padding: 5px 0;'>🔧 Manutenção/Desgaste:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_manutencao:.2f}</td></tr>
                    <tr style='border-bottom: 1px dashed #dee2e6;'><td style='padding: 5px 0; font-weight: bold;'>📉 Custo Total da Rota:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_total:.2f}</td></tr>
                    <tr><td style='padding: 10px 0 5px 0; font-size: 18px; font-weight: bold;'>💵 Lucro Líquido Real:</td><td style='text-align: right; font-size: 18px; font-weight: bold; color: {cor_lucro};'>R$ {saldo_liquido:.2f}</td></tr>
                    <tr><td style='padding: 5px 0;'>📍 Lucro Líquido por km:</td><td style='text-align: right; font-weight: bold; color: {cor_lucro};'>R$ {ganho_por_km:.2f}/km (Bruto: R$ {bruto_por_km:.2f}/km)</td></tr>
                    <tr><td style='padding: 5px 0;'>⏱️ Lucro Líquido por hora:</td><td style='text-align: right; font-weight: bold; color: {cor_lucro};'>R$ {ganho_por_hora:.2f}/h (Bruto: R$ {bruto_por_hora:.2f}/h)</td></tr>
                    <tr><td style='padding: 5px 0;'>📈 Margem Líquida:</td><td style='text-align: right; font-weight: bold;'>{margem:.1f}%</td></tr>
                </table>
                <div class='result-box {classe_status}'>
                    {status_txt}
                </div>
            </div>
            """
            st.markdown(html_resultado, unsafe_allow_html=True)

            # Salva no histórico da sessão
            st.session_state.historico.append({
                "Veículo": modelo_selecionado,
                "Dist. (km)": distancia,
                "Tempo (min)": tempo_min,
                "Recebido (R$)": valor_corrida,
                "Custo (R$)": round(custo_total, 2),
                "Lucro (R$)": round(saldo_liquido, 2)
            })
            st.toast("Rota salva no histórico do dia!", icon="✅")

# ==========================================
# ABA 2: HISTÓRICO DO DIA
# ==========================================
with aba_historico:
    st.subheader("Resumo das Corridas Calculadas Hoje")
    if len(st.session_state.historico) == 0:
        st.info("Nenhuma corrida calculada ainda. Use a aba 'Calcular Rota' para começar.")
    else:
        df = pd.DataFrame(st.session_state.historico)
        
        total_recebido = df["Recebido (R$)"].sum()
        total_custos = df["Custo (R$)"].sum()
        total_lucro = df["Lucro (R$)"].sum()
        total_minutos = df["Tempo (min)"].sum()

  

 

           
