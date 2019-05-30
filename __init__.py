# 
import pandas as pd
import requests as rq
import numpy as np
import re


def download_data(url,option='xls',gid=None):
    """
    extrai planilha do google sheets utilizando a API google sheets.
    
    EXEMPLO: download_data('https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/',gid='0',option='csv')
    
    option: mime do arquivo. opções são xls e csv
    url   : url da planhilha. 
    gid   : id da planilha. Necessário para formato csv
    saida : dados da requisição GET
    """
    flavor_url = '/export?download'
    if (option == 'csv') & (gid is not None):
        flavor_url = '/export?format=csv&gid=%s' % gid
    base_url = 'https://docs.google.com/spreadsheets/d/'
    flag = url.find(base_url)
    if flag  <0:
        return None #'incorrect url. Try %s/KEY/' % base_url
    end_key = url[len(base_url):].find('/')
    if end_key < 0:
        return None #'incorrect url. Missing KEY. Try %s/KEY/' % base_url
    download_url = base_url+ url[len(base_url):(end_key+len(base_url))] + flavor_url
    #
    # TODO: usar memoização para evitar multiplos downloads
    #

    #
    # TODO: colocar clausulas *try* para erros de conexao
    #
    return rq.get(download_url)

def create_dataframes_from_excel(url=None,xls=None):
    """
    cria um conjunto de dataframes do pandas a partir de uma url valida para o google sheets 
    ou nome de arquivo excel
    
    parametros:
    url :: url que aponta para a planilha do google. EX: https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/
    xls :: caminho para o arquivo xls
    df  :: saida. lista de dataframes
    """
    if url:
        arquivo = download_data(url=url,option='xls') # TODO colocar uma clausula *if arquivo: ...*
        xls = 'arquivo_url.xls'
        with open(xls,'wb') as f:
            f.write(arquivo.content)
    # a string xls existe e tem valor definido
    if xls:
        sheets = pd.ExcelFile(xls).sheet_names # obtem todas as planilhas
        df = [pd.read_excel(xls, sheet_name = i) for i in sheets] # para cada planilha é criado um dataframe
        return df
    return None

def create_dataframes_from_csv(sheets=[],url=None,gids=None,sep=','):
    """
    Cria um conjunto de dataframes do pandas a partir de arquivos csv (sheets).
    Se os nomes dos arquivos csv não forem passados, assume-se que as planilhas
    serão baixadas por meio da url e das IDs das planilhas
    
    parametros:
    sheets :: lista com os caminhos dos arquivos csv
    url    :: url da planilha do google
    gids   :: lista com ID de cada planilha (não é a key da planilha)
    sep    :: separador dos arquivos csv
    df     :: saída. lista de dataframes
    """
    df=[]
    if sheets:
        #
        # TODO : chamar sys para verificar se arquivo csv existe
        #
        for sheet in sheets:
            df.append( pd.read_csv( sheet ,sep = sep ) )
        return df

    if (url is not None) & (gids is not None):
        sheets=[]
        for x in gids:
            arquivo = download_data(url=url,gid=x,option='csv')
            sheets.append( arquivo.text )
    from io import StringIO
    for sheet in sheets:
        df.append( pd.read_csv( StringIO(sheet) ,sep = sep ) )
    return df


def sanitize_dataframes_nan(*dataframe):
    """
    substitui os locais sem preenchimento (NaN) por espaço vazio
    
    parametro:
    dataframe :: conjunto de dataframes
    """
    for data in dataframe:
        data.fillna('', inplace=True)
    return

## todo: quando tiver uma letra no numero de telefone retornar uma mensagem de erro e zerar o telefone
def sanitize_phone_brazil(phonenumber):
    """
    transforma o número de telefone para o formato +55DDDNUMERO
    
    parametros:
    phonenumber :: numero do telefone a ser formatado
    numero      :: saida
    """
    number_size = 10      # configuração dos número:      3DDD 3NUMEROS-4NUMEROS.
    number_size_max = 12  # configuração dos número: 2DDI 3DDD 3NUMEROS-4NUMEROS
    res = re.findall('([0-9]+)',str(phonenumber))
    number=''.join(res)
    if (len(number) < number_size) or (len(number) > number_size_max):
        return ''
    return '+55'+number[-number_size:]


def sanitize_money(money):
    """
    transforma o dinheiro para o formato NUMEROS_REAIS,NUMEROS_CENTAVOS
    
    parametros:
    money  :: valor do dinheiro a ser formatado
    """
    moneys = re.findall( '([0-9]+)',str(money))
    cents  = '00'
    if (len(moneys) > 0):
        if (len(moneys)>1) & (len(moneys[-1]) < 3) : # centavos tem no maximo 2 digitos
            cents = ''.join(moneys[-1])
            cents = cents.ljust(2,'0')
            moneys.pop(-1)
        return ''.join(moneys)+','+cents
    return ''


def sanitize_discount(desconto):
    """
    retira os caracteres inválidos dos valores de desconto, substituindo-os por 0
    
    parametro:
    desconto :: valor do desconto
    """
    return ''.join(re.findall('[0-9]+', str(desconto))) or '0'


def convert_tointeger(var_input):
    """
    converte as entradas do dinheiro para inteiro
    
    parametro:
    var_input :: valor do dinheiro
    """
    return int(sanitize_money(var_input).replace(',',''))


def convert_tostring(var_input):
    """
    converte a entrada para string
    
    parametro:
    var_input :: valor do dinheiro
    
    """
    return "%.2f" % var_input



def final_value(value,discount='0'):
    """
    calcula o valor com o desconto
    
    parametros:
    value    :: valor do dinheiro
    discount :: valor do desconto
    saida    :: valor com desconto
    """
    money = np.float64(convert_tointeger(value))/100.0
    delta = np.float64(discount)/100.0
    return sanitize_money(convert_tostring(money*(1e0 - delta)))

def merge_by_key(df0,df1,key0='id',key1='user_id',how='left'):
    """
    retorna a junção de duas tabelas de acordo com campos em comum key0 e key1
    
    df0  :: dataframe alvo.
    df1  :: dataframe auxiliar
    key0 :: string. chave de df0.
    key1 :: string. chave de df1.
    how  :: string. maneira como o merge é feito. pode ser left, right, inner
    saida:: df0 é atualizada com os campos correspondentes de df1
    """
    #return df0.merge(df1,left_on=key0,right_on=key1,how=how)
    return pd.merge(df0,df1,left_on=key0,right_on=key1,how=how)














## funções de teste:

if __name__ == "__main__":
    
    
    def debug_excel():
        url = 'https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/export?download'
        df = create_dataframes_from_excel(url=url)
        if df:
            return True
        return False

    def debug_csv():
        url = 'https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/'
        df = create_dataframes_from_csv(url=url,gids=['0','822929440'])
        if df:
            return True
        return False
    
    def debug_sanitize_nan():
        url = 'https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/export?download'
        df = create_dataframes_from_excel(url=url)
        sanitize_dataframes_nan(*df)
        #
        # TODO:
        #      df.isna() retorna True mesmo quando não há valores NaN
        #      workaround: define função (poderia ser lambda tbm)
        #      que usa .isna() em cada coluna do dataframe
        #
        def helper(data):
            return any( [ any(data[x].isna()) for x in data.columns] )
        return not any( [helper(data) for data in df] )
    
    def debug_sanitize(tentativa,f):
        # tentativa é um dicionário que contém as chaves num formato, e o dado correspondente no formato desejado
        return not any( [ not (f(x) == tentativa[x]) for x in tentativa] )
    
    def debug_sanitize_money():
        # tentativa é um dicionário que contém as chaves num formato, e o dado correspondente no formato desejado
        tentativa={'1.1':'1,10', '7':'7,00' , '1.230':'1230,00' , '1.230.20': '1230,20' }
        return debug_sanitize(tentativa,sanitize_money)
    def debug_sanitize_phone_brazil():
        # tentativa é um dicionário que contém as chaves num formato, e o dado correspondente no formato desejado
        tentativa={'+559991234567':'+559991234567','(999)1234567':'+559991234567','999123456':'','+5999123-4567':'+559991234567', '9'*13:''}
        return debug_sanitize(tentativa,sanitize_phone_brazil)
    def debug_sanitize_discount():
        # tentativa é um dicionário que contém as chaves num formato, e o dado correspondente no formato desejado
        tentativa={'3':'3','30':'30','-':'0'}
        return debug_sanitize(tentativa,sanitize_discount)
    def debug_merge_by_key():
        url = 'https://docs.google.com/spreadsheets/d/1N6JFMIQR71HF5u5zkWthqbgpA8WYz_0ufDGadeJnhlo/'
        df = create_dataframes_from_csv(url=url,gids=['0','822929440'])
        DF = merge_by_key(df[0],df[1],how='inner')
        return (len(DF) == len(df[1]))
    
    #------------------------------------------------
    print("Starting tests::")
    print('Reading excel file from internet ...',end=" ") # end remove o caracter de nova linha # TODO usar zfill
    print(debug_excel())
    print('Reading csv files from internet  ...',end=' ')
    print(debug_excel())
    print('Sanitizing dataframes            ...',end=' ')
    print(debug_sanitize_nan())
    print('Sanitizing money                 ...',end=' ')
    print(debug_sanitize_money())
    print('Sanitizing telephone             ...',end=' ')
    print(debug_sanitize_phone_brazil())
    print('Sanitizing discount              ...',end=' ')
    print(debug_sanitize_discount())
    print('Checking merge                   ...',end=' ')
    print(debug_merge_by_key())
    
    
