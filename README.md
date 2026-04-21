# Controle Loja 5 - Railway + celular

Aplicativo em Python + Flask para registrar mercadorias separando `ESTOQUE` e `LOJA 5`, com layout adaptado para celular e visual inspirado no site do Supermercados Alvorada.

## O que ele faz
- lê ou recebe o código de barras
- pergunta o nome do produto
- pergunta a quantidade
- marca a origem: `ESTOQUE` ou `LOJA 5`
- gera relatório agrupado
- exporta CSV
- abre uma versão pronta para impressão / PDF
- permite criar vários inventários separados
- funciona melhor no celular com layout responsivo
- permite editar ou excluir lançamentos individuais em caso de erro

## Visual
A versão atual foi ajustada para:
- comportamento melhor no celular
- cabeçalho e hero inspirados no estilo do site da rede
- botões grandes para toque
- relatório em cartões no mobile e tabela no desktop

## Como instalar
```bash
pip install -r requirements.txt
```

## Como rodar localmente
```bash
python app.py
```

Depois abra no navegador:
- no próprio computador: `http://127.0.0.1:5000`
- no celular na mesma rede: `http://IP_DO_COMPUTADOR:5000`

## Como subir no Railway
1. envie os arquivos para um repositório GitHub
2. conecte o repositório no Railway
3. crie a variável `SECRET_KEY`
4. adicione um volume montado em `/data`
5. publique o projeto

## Observação importante sobre a câmera
A leitura pela câmera depende do navegador do celular e do suporte do navegador à API de leitura de código de barras.
Se não funcionar:
1. use a opção de foto
2. ou digite o código manualmente

## Estrutura
- `app.py` -> sistema completo
- `static/logo_alvorada.png` -> logo usada no cabeçalho
- `static/hero_loja.jpg` -> imagem principal do topo
- `dados.db` -> banco SQLite criado automaticamente
- `requirements.txt` -> dependências
- `railway.toml` -> configuração de deploy
- `start.sh` -> comando de inicialização no Railway
