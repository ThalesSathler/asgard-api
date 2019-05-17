# Worker de Auto Scaling de aplicações do ASGARD

## Configurações de aplicações

```json
{
    "asgard.autoscale.cpu": 0.3,
    "asgard.autoscale.mem": 0.8,
    "asgard.autoscale.ignore": "cpu;mem;all"
}
```

Labels autoscale.cpu e autoscale.mem indicam os parâmetros a serem utilizados para scale de CPU e memória, respectivamente. Não é necessário que ambos estejam presentes, a ausência de um deles indica que o parâmetro não deve ser processado pelo autoscaler e a ausência de ambos indica que o autoscaler não deve fazer scaling da aplicação.

Labels de ignore indicam que algum label existente deve ser ignorado, sendo que o parâmetro "all" indica que o autoscaler não deve atuar na aplicação. Esse parâmetro separado será util para desabilitar o autoscaler temporariamente sem ser necessário remover labels já definidas