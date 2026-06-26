# Exemplo de uso

> Substituir o conteúdo abaixo pelos exemplos reais da habilidade.

## Cenário básico

```python
from mana_habilidade_placeholder.core import placeholder_function

resultado = placeholder_function("entrada de exemplo")
print(resultado)
# >>> "entrada de exemplo processada"
```

## Integração com outro agente Maná

```python
# Em um agente conversacional Maná
from mana_habilidade_placeholder.core import placeholder_function
from mana_llm import Claude
from mana_whatsapp import Bot

bot = Bot()
claude = Claude()

def handle_message(msg):
    entrada = msg.text
    processado = placeholder_function(entrada)
    resposta = claude.complete(f"Comente sobre: {processado}")
    bot.send(msg.chat_id, resposta)
```

## Casos especiais

[Documentar edge cases / combinações úteis aqui]

## Como NÃO usar

[Documentar anti-padrões aqui]
