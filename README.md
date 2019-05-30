# desafio

Desafio de migração de dados

## Organização dos arquivos do pacote desafio:

```bash
└── desafio
    ├── __init__.py
    ├── LICENSE
    └── README.md
```

## Requerimentos:

* Pandas
* Numpy
* Requests
* Re (Expressões Regulares)

## Uso:

* Como __main__: inicia o modo de teste unitário
* Caso contrário: funções

### Funções:

```python

## Carregando dataframes:
 'download_data'
 'create_dataframes_from_csv'
 'create_dataframes_from_excel'


## Sanitização:
 'sanitize_dataframes_nan'
 'sanitize_discount'
 'sanitize_money'
 'sanitize_phone_brazil'
 
## Operações com números (int e float) e strings:
 'convert_tointeger' 
 'convert_tostring'
 'final_value' # cálculo do valor com desconto

## Associação de 
 'merge_by_key'

## testes:
 'debug_csv'
 'debug_excel'
 'debug_sanitize'
 'debug_sanitize_discount'
 'debug_sanitize_money'
 'debug_sanitize_nan'
 'debug_sanitize_phone_brazil'
 'debug_merge_by_key'

```
