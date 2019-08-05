from abc import ABC, abstractclassmethod
from typing import Generic, TypeVar

AsgardModel = TypeVar("AsgardModel")
ClientModel = TypeVar("ClientModel")


class ModelConverterInterface(Generic[AsgardModel, ClientModel], ABC):
    """
    Essa interface deve ser usada por modelos declarados nos backends
    para que a conversão entre AsgardModel e ClientModel (e o inverso) possa
    ser feita.

    Isso existe para que o core do código da asgard API não precise saber
    detalhes de implementação dos modelos dos backends que estão sendo usados.

    Exemplo:
      Podemos ter múltiplos Backends que gerenciam Aplicações. Cada backend pode ser sua API que retorna seus próprios recursos. Para o código do asgard só deve existir um modelo: `asgard.models.app.App`.
      Se o Marathon retorna suas Apps com um JSON `A`, o ModelConverter serve para fazer as seguintes traduções: `A -> asgard.models.app.App` e `asgard.models.app.App -> A`.
      Se o k8s rerorna suas apps com um JSON `B`. Teremos outro ModelConverter que vai fazer a tradução `B` <-> `asgard.models.app.App`.

    """

    @abstractclassmethod
    def to_asgard_model(cls, other: ClientModel) -> AsgardModel:
        """
        Converte um ClientModel em AsgardModel.

        O objetivo desse método é copiar todos os campos do ClientModel em questão
        para seus respectivos campos em um Asgard Model.
        """
        raise NotImplementedError

    @abstractclassmethod
    def to_client_model(cls, other: AsgardModel) -> ClientModel:
        """
        Converte um AsgardModel para ClientModel.

        O objetivo desse método é copiar todos os campos do AsgardModel em questão
        para seus respectivos campos em um ClientModel.
        """
        raise NotImplementedError
