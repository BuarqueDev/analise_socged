import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def formatar_data_completa(data_inicio, data_fim):
    """
    Formata o período completo de forma legível, 
    garantindo que toda a data seja visível
    """
    # Converte para strings formatadas com dia, mês e ano completos
    data_inicio_str = data_inicio.strftime('%d/%m/%Y')
    data_fim_str = data_fim.strftime('%d/%m/%Y')
    
    return f"{data_inicio_str} até {data_fim_str}"


def processar_dataframe(df):
    """Processa o DataFrame para análise."""
    # Converte coluna de data para datetime
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
    
    # Barra lateral de configurações
    st.sidebar.header('🛠️ Configurações')
    
    arquivo_carregado = st.file_uploader('Carregue sua planilha', 
                                         type=['xlsx', 'csv', 'txt'])
    
    if arquivo_carregado is not None:
        try:
            df = carregar_dataframe(arquivo_carregado)
            df = processar_dataframe(df)
            
            # Abas de análise
            abas = st.tabs([
                '📈 Visão Geral', 
                '👥 Análise por Usuário', 
                '🏢 Análise por Empresa', 
                '⏰ Análise Temporal', 
                '🔍 Detalhamento Completo'
            ])
            
            with abas[0]:  # Visão Geral
                col1, col2, col3 = st.columns(3)
                col1.metric('🔢 Total de Registros', len(df))
                col2.metric('👥 Usuários Únicos', df['Usuário'].nunique())
                col3.metric('📅 Período', 
                            formatar_data_completa(df['Data'].min(), df['Data'].max()))
                
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
            
            with abas[1]:  # Análise por Usuário
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
            
            with abas[2]:  # Análise por Empresa
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
            
            with abas[3]:  # Análise Temporal
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
            
            with abas[4]:  # Detalhamento Completo
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
        
        except Exception as e:
            st.error(f'Erro ao processar arquivo: {e}')

if __name__ == '__main__':
    main()