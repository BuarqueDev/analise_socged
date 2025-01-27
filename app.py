import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import xlsxwriter
import io

# Configurações e constantes
META_DIARIA = 100
CONTATO_EMAIL = "erikbuarque.10@gmail.com"
VERSAO = "1.0.0"

def criar_excel_dashboard(df):
    """Cria um dashboard no Excel com as análises principais."""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Aba de dados brutos
        df.to_excel(writer, sheet_name='Dados', index=False)
        
        # Aba de análises
        analises = pd.DataFrame({
            'Métrica': [
                'Total de Registros',
                'Média Diária',
                'Média Semanal',
                'Média Mensal',
                'Dias Batendo Meta',
                '% Dias Batendo Meta'
            ],
            'Valor': [
                len(df),
                df.groupby(df['Data'].dt.date).size().mean(),
                df.groupby(pd.Grouper(key='Data', freq='W')).size().mean(),
                df.groupby(pd.Grouper(key='Data', freq='M')).size().mean(),
                len(df.groupby(df['Data'].dt.date).size()[df.groupby(df['Data'].dt.date).size() >= META_DIARIA]),
                (len(df.groupby(df['Data'].dt.date).size()[df.groupby(df['Data'].dt.date).size() >= META_DIARIA]) / 
                 len(df.groupby(df['Data'].dt.date).size()) * 100)
            ]
        })
        analises.to_excel(writer, sheet_name='Análises', index=False)
        
        # Configurações do workbook
        workbook = writer.book
        worksheet = writer.sheets['Análises']
        
        # Formato para números
        numero_format = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.set_column('B:B', 15, numero_format)
        
        # Criar gráficos
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Registros por Data',
            'categories': '=Dados!$A$2:$A$' + str(len(df) + 1),
            'values': '=Dados!$B$2:$B$' + str(len(df) + 1),
        })
        worksheet.insert_chart('D2', chart)
    
    output.seek(0)
    return output

def calcular_metricas(df, periodo='D'):
    """Calcula métricas básicas para diferentes períodos (D=diário, W=semanal, M=mensal)."""
    return df.groupby(pd.Grouper(key='Data', freq=periodo)).size()

def formatar_data_completa(data_inicio, data_fim):
    """Formata o período completo de forma legível."""
    return f"{data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"

def processar_dataframe(df):
    """Processa o DataFrame para análise."""
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    return df

def carregar_dataframe(arquivo_carregado):
    """Carrega DataFrame de diferentes formatos."""
    if arquivo_carregado.name.endswith('.xlsx'):
        return pd.read_excel(arquivo_carregado)
    elif arquivo_carregado.name.endswith(('.csv', '.txt')):
        return pd.read_csv(arquivo_carregado, sep='\t', encoding='utf-8')
    else:
        raise ValueError("Formato de arquivo não suportado")

def main():
    st.set_page_config(layout="wide", page_title="Análise de Dados")
    st.title('📊 Análise Inteligente de Dados')
    
    # Informações sobre o programa
    with st.sidebar.expander("ℹ️ Sobre o Software"):
        st.write("""
        ### Versão
        {}
        
        ### Contato
        - 📧 Email: {}
        - 💬 Feedback: [Link do Forms]
        - 🐛 Reportar Bugs: https://github.com/BuarqueDev/
        
        ### Documentação
        [Link para documentação completa]
        """.format(VERSAO, CONTATO_EMAIL))
    
    # Barra lateral de configurações
    st.sidebar.header('🛠️ Configurações')
    
    arquivo_carregado = st.file_uploader('Carregue sua planilha', type=['xlsx', 'csv', 'txt'])
    
    if arquivo_carregado is not None:
        try:
            df = carregar_dataframe(arquivo_carregado)
            df = processar_dataframe(df)
            
            # Filtros de data
            st.sidebar.subheader('📅 Filtros de Data')
            filtro_tipo = st.sidebar.selectbox(
                'Tipo de Filtro',
                ['Período Completo', 'Mês Específico', 'Intervalo Personalizado']
            )
            
            if filtro_tipo == 'Mês Específico':
                mes_selecionado = st.sidebar.selectbox(
                    'Selecione o Mês',
                    df['Data'].dt.strftime('%Y-%m').unique()
                )
                df = df[df['Data'].dt.strftime('%Y-%m') == mes_selecionado]
            elif filtro_tipo == 'Intervalo Personalizado':
                data_inicio = st.sidebar.date_input('Data Inicial', df['Data'].min())
                data_fim = st.sidebar.date_input('Data Final', df['Data'].max())
                df = df[(df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)]
            
            # Abas de análise
            abas = st.tabs([
                '📈 Visão Geral', 
                '📊 Análise de Metas',
                '👥 Análise por Usuário', 
                '🏢 Análise por Empresa', 
                '⏰ Análise Temporal',
                '🔍 Detalhamento Completo'
            ])
            
            with abas[0]:  # Visão Geral
                col1, col2, col3, col4 = st.columns(4)
                
                # Métricas diárias, semanais e mensais
                media_diaria = calcular_metricas(df, 'D').mean()
                media_semanal = calcular_metricas(df, 'W').mean()
                media_mensal = calcular_metricas(df, 'M').mean()
                
                col1.metric('📊 Média Diária', f'{media_diaria:.1f}')
                col2.metric('📈 Média Semanal', f'{media_semanal:.1f}')
                col3.metric('📅 Média Mensal', f'{media_mensal:.1f}')
                col4.metric('👥 Usuários Únicos', df['Usuário'].nunique())
                
                col4, col5 = st.columns(2)
                with col4:
                    # Distribuição de Ações
                    contagem_acoes = df['Ação'].value_counts()
                    fig_acoes = px.pie(
                        values=contagem_acoes.values, 
                        names=contagem_acoes.index, 
                        title='Distribuição de Tipos de Ação',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_acoes.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_acoes, use_container_width=True)
                
                with col5:
                    # Top Usuários por Número de Ações
                    top_usuarios = df['Usuário'].value_counts().head(5)
                    fig_usuarios = px.bar(
                        x=top_usuarios.values, 
                        y=top_usuarios.index, 
                        orientation='h',
                        title='Top 5 Usuários por Número de Ações',
                        labels={'x': 'Número de Ações', 'y': 'Usuário'},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_usuarios, use_container_width=True)
            
            with abas[1]:  # Análise de Metas
                registros_diarios = df.groupby(df['Data'].dt.date).size()
                dias_meta = registros_diarios[registros_diarios >= META_DIARIA]
                
                col1, col2, col3 = st.columns(3)
                col1.metric('🎯 Meta Diária', META_DIARIA)
                col2.metric('📅 Dias Batendo Meta', len(dias_meta))
                col3.metric('✨ % Sucesso', f'{(len(dias_meta) / len(registros_diarios) * 100):.1f}%')
                
                # Gráfico de desempenho vs meta
                fig_meta = go.Figure()
                fig_meta.add_trace(go.Scatter(
                    x=registros_diarios.index,
                    y=registros_diarios.values,
                    name='Registros',
                    line=dict(color='#636EFA')
                ))
                fig_meta.add_trace(go.Scatter(
                    x=registros_diarios.index,
                    y=[META_DIARIA] * len(registros_diarios),
                    name='Meta',
                    line=dict(color='red', dash='dash')
                ))
                fig_meta.update_layout(title='Desempenho Diário vs Meta')
                st.plotly_chart(fig_meta, use_container_width=True)
            
            with abas[2]:  # Análise por Usuário
                usuario_selecionado = st.selectbox(
                    'Selecione um Usuário',
                    df['Usuário'].unique()
                )
                
                df_usuario = df[df['Usuário'] == usuario_selecionado]
                
                col6, col7 = st.columns(2)
                with col6:
                    # Ações do Usuário
                    acoes_usuario = df_usuario['Ação'].value_counts()
                    fig_acoes_usuario = px.pie(
                        values=acoes_usuario.values,
                        names=acoes_usuario.index,
                        title=f'Distribuição de Ações - {usuario_selecionado}',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_acoes_usuario.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_acoes_usuario, use_container_width=True)
                
                with col7:
                    # Empresas do Usuário
                    empresas_usuario = df_usuario['Nome Empresa'].value_counts()
                    fig_empresas_usuario = px.bar(
                        x=empresas_usuario.values,
                        y=empresas_usuario.index,
                        orientation='h',
                        title=f'Empresas Trabalhadas - {usuario_selecionado}',
                        labels={'x': 'Número de Ações', 'y': 'Empresa'},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_empresas_usuario, use_container_width=True)
                
                # Detalhes do Usuário
                st.subheader(f'Detalhes de {usuario_selecionado}')
                st.dataframe(df_usuario)
            
            with abas[3]:  # Análise por Empresa
                empresa_selecionada = st.selectbox(
                    'Selecione uma Empresa',
                    df['Nome Empresa'].unique()
                )
                
                df_empresa = df[df['Nome Empresa'] == empresa_selecionada]
                
                col8, col9 = st.columns(2)
                with col8:
                    # Ações da Empresa
                    acoes_empresa = df_empresa['Ação'].value_counts()
                    fig_acoes_empresa = px.pie(
                        values=acoes_empresa.values,
                        names=acoes_empresa.index,
                        title=f'Distribuição de Ações - {empresa_selecionada}',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_acoes_empresa.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_acoes_empresa, use_container_width=True)
                
                with col9:
                    # Usuários da Empresa
                    usuarios_empresa = df_empresa['Usuário'].value_counts()
                    fig_usuarios_empresa = px.bar(
                        x=usuarios_empresa.values,
                        y=usuarios_empresa.index,
                        orientation='h',
                        title=f'Usuários Ativos - {empresa_selecionada}',
                        labels={'x': 'Número de Ações', 'y': 'Usuário'},
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(fig_usuarios_empresa, use_container_width=True)
                
                # Detalhes da Empresa
                st.subheader(f'Detalhes de {empresa_selecionada}')
                st.dataframe(df_empresa)
            
            with abas[4]:  # Análise Temporal
                # Registros por Data
                registros_por_data = df.groupby(df['Data'].dt.date).size()
                fig_registros_data = px.line(
                    x=registros_por_data.index,
                    y=registros_por_data.values,
                    title='Registros por Data',
                    labels={'x': 'Data', 'y': 'Número de Registros'},
                    color_discrete_sequence=['#636EFA']
                )
                st.plotly_chart(fig_registros_data, use_container_width=True)
            
            with abas[5]:  # Detalhamento Completo
                st.dataframe(df)
                
                # Filtros adicionais
                st.sidebar.subheader('Filtros Avançados')
                filtro_acao = st.sidebar.multiselect(
                    'Filtrar por Ação',
                    df['Ação'].unique()
                )
                
                if filtro_acao:
                    df_filtrado = df[df['Ação'].isin(filtro_acao)]
                    st.dataframe(df_filtrado)

                # Botão para download do dashboard Excel
            excel_data = criar_excel_dashboard(df)
            st.download_button(
                label="📥 Download Dashboard Excel",
                data=excel_data,
                file_name="dashboard_analise.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f'Erro ao processar arquivo: {e}')

if __name__ == '__main__':
    main()