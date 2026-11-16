import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Calculadora de Lucro - Motorista App", page_icon="🚗", layout="centered")

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
    .afiliado-box {
        background-color: #f1f3f5;
        border-left: 4px solid #0d6efd;
        padding: 12px;
        border-radius: 6px;
        margin-top: 20px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='app-title'>🚗 Calculadora de Rota & Lucro Real</h2>", unsafe_allow_html=True)

# Abas para organizar o App
aba_calc, aba_historico, aba_loja = st.tabs(["📊 Calcular Rota", "📅 Meu Dia (Histórico)", "🛒 Equipamentos"])

# ==========================================
# ABA 1: CALCULADORA DE ROTA
# ==========================================
with aba_calc:
    opcoes_combustivel = {
        'Gasolina': 5.80,
        'Etanol': 3.90,
        'Diesel': 6.10,
        'GNV': 4.70,
        'Outro (Definir)': 0.0
    }

    combustivel_selecionado = st.selectbox("Combustível:", list(opcoes_combustivel.keys()))
    preco_padrao = opcoes_combustivel[combustivel_selecionado]

    col1, col2 = st.columns(2)
    with col1:
        preco_comb = st.number_input("Preço Litro/m³ (R$):", min_value=0.0, value=float(preco_padrao) if preco_padrao > 0 else 5.00, step=0.10, format="%.2f")
        distancia = st.number_input("Distância Total (km):", min_value=0.0, value=15.0, step=1.0, format="%.1f")

    with col2:
        consumo = st.number_input("Consumo (km/L ou m³):", min_value=0.0, value=10.0, step=0.5, format="%.1f")
        valor_corrida = st.number_input("Valor da Corrida (R$):", min_value=0.0, value=35.0, step=1.0, format="%.2f")

    custo_km_manut = st.slider("Custo estimado de manutenção/desgaste por km (R$):", min_value=0.05, max_value=0.50, value=0.20, step=0.05)

    if st.button("Analisar Viabilidade", type="primary", use_container_width=True):
        if consumo <= 0 or preco_comb <= 0 or distancia <= 0 or valor_corrida <= 0:
            st.markdown("<div class='result-box status-danger'>⚠️ Preencha todos os campos com valores maiores que zero!</div>", unsafe_allow_html=True)
        else:
            custo_combustivel = (distancia / consumo) * preco_comb
            custo_manutencao = distancia * custo_km_manut
            custo_total = custo_combustivel + custo_manutencao
            saldo_liquido = valor_corrida - custo_total
            margem = (saldo_liquido / valor_corrida) * 100
            ganho_por_km = saldo_liquido / distancia

            if saldo_liquido < 0:
                classe_status = "status-danger"
                status_txt = "🚨 PREJUÍZO! Não vale a pena aceitar essa rota."
            elif margem < 30:
                classe_status = "status-warn"
                status_txt = "⚠️ RAZOÁVEL. Retorno baixo para o desgaste do veículo."
            else:
                classe_status = "status-ok"
                status_txt = "✅ EXCELENTE! Corrida altamente lucrativa."

            cor_lucro = '#28a745' if saldo_liquido > 0 else '#dc3545'

            html_resultado = f"""
            <div style='margin-top: 15px; border-top: 1px solid #dee2e6; padding-top: 15px;'>
                <table style='width: 100%; border-collapse: collapse; font-size: 15px;'>
                    <tr><td style='padding: 5px 0;'>⛽ Combustível:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_combustivel:.2f}</td></tr>
                    <tr><td style='padding: 5px 0;'>🔧 Manutenção/Desgaste:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_manutencao:.2f}</td></tr>
                    <tr style='border-bottom: 1px dashed #dee2e6;'><td style='padding: 5px 0; font-weight: bold;'>📉 Custo Total:</td><td style='text-align: right; font-weight: bold;'>R$ {custo_total:.2f}</td></tr>
                    <tr><td style='padding: 10px 0 5px 0; font-size: 18px; font-weight: bold;'>💵 Lucro Líquido Real:</td><td style='text-align: right; font-size: 18px; font-weight: bold; color: {cor_lucro};'>R$ {saldo_liquido:.2f}</td></tr>
                    <tr><td style='padding: 5px 0;'>📍 Lucro por km rodado:</td><td style='text-align: right; font-weight: bold;'>R$ {ganho_por_km:.2f}/km</td></tr>
                    <tr><td style='padding: 5px 0;'>📈 Margem de Lucro:</td><td style='text-align: right; font-weight: bold;'>{margem:.1f}%</td></tr>
                </table>
                <div class='result-box {classe_status}'>
                    {status_txt}
                </div>
            </div>
            """
            st.markdown(html_resultado, unsafe_allow_html=True)

            # Salva automaticamente no histórico da sessão
            st.session_state.historico.append({
                "Distância (km)": distancia,
                "Recebido (R$)": valor_corrida,
                "Custo Total (R$)": round(custo_total, 2),
                "Lucro Líquido (R$)": round(saldo_liquido, 2)
            })
            st.toast("Corrida adicionada ao histórico do dia!", icon="✅")

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
        total_custos = df["Custo Total (R$)"].sum()
        total_lucro = df["Lucro Líquido (R$)"].sum()
        total_km = df["Distância (km)"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Bruto", f"R$ {total_recebido:.2f}")
        m2.metric("Custos", f"R$ {total_custos:.2f}")
        m3.metric("Lucro Real", f"R$ {total_lucro:.2f}")

        st.dataframe(df, use_container_width=True)

        if st.button("🗑️ Limpar Histórico do Dia"):
            st.session_state.historico = []
            st.rerun()

# ==========================================
# ABA 3: MONETIZAÇÃO (AFILIADOS)
# ==========================================
with aba_loja:
    st.subheader("🛠️ Equipamentos Recomendados para Motoristas")
    st.write("Aumente sua segurança e conforto nas corridas com itens testados:")

    # Substitua os links "#" pelos seus links de afiliado da Amazon, Shopee ou Mercado Livre
    st.markdown("""
    * 📱 **[Suporte Veicular Magnético Ultra Firme](https://amazon.com.br)** – Não cai em buracos e facilita aceitar corridas rápido.
    * ⚡ **[Carregador Veicular Turbo 38W (USB-C + USB)](https://mercadolivre.com.br)** – Mantém o celular em 100% mesmo com GPS e brilho no máximo.
    * 📹 **[Câmera Veicular (Dashcam) Full HD](https://shopee.com.br)** – Segurança indispensável contra batidas e passageiros mal-intencionados.
    * 💺 **[Encosto Ortopédico Massageador para Banco](https://amazon.com.br)** – Evita dores nas costas após 8h+ dirigindo.
    """)
    st.caption("Nota: Ao comprar pelos links acima, você apoia a manutenção gratuita deste aplicativo sem pagar nada a mais por isso.")

# ==========================================
# RODAPÉ: APOIO VIA PIX
# ==========================================
st.divider()
with st.expander("☕ Essa calculadora te ajudou a evitar prejuízo? Apoie o projeto!"):
    st.write("Este aplicativo é **100% gratuito**. Se ele te ajudou a lucrar mais hoje, considere contribuir com qualquer valor via Pix para manter o servidor no ar:")
    # Coloque a sua chave Pix real abaixo
    st.code("alexdesouzabispo@gmail.com", language="text")
    st.caption("Copie a chave acima e cole no aplicativo do seu banco. Muito obrigado e boas corridas!")
