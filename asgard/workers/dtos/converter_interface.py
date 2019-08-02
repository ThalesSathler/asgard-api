from abc import ABC, abstractclassmethod
from typing import Generic, TypeVar, List

ModelObject = TypeVar("ModelObject")
DtoObject = TypeVar("DtoObject")


class Converter(Generic[ModelObject, DtoObject], ABC):
    """
    Essa interface deve ser usada em casos onde o software se comunique com APIs externas
    para que seja feita uma conversão entre os DTOs retornados pela API e os modelos
    utilizados pelo software.

    Isso existe para que nao haja dependência entre as interfaces externas e o core do código

    Exemplo:
      Podemos ter múltiplos Backends que gerenciam Aplicações. Cada backend pode ser sua API que retorna seus próprios recursos. Para o código do asgard só deve existir um modelo: `asgard.models.app.App`.
      Se o Marathon retorna suas Apps com um JSON `A`, o ModelConverter serve para fazer as seguintes traduções: `A -> asgard.models.app.App` e `asgard.models.app.App -> A`.
      Se o k8s rerorna suas apps com um JSON `B`. Teremos outro ModelConverter que vai fazer a tradução `B` <-> `asgard.models.app.App`.

    """

    @abstractclassmethod
    def to_model(cls, dto_object: DtoObject) -> ModelObject:
        """
        Converte um objeto DTO para um objeto do modelo.

        O objetivo desse método é copiar todos os campos do DTO em questão
        para seus respectivos campos no modelo.
        """
        raise NotImplementedError

    @abstractclassmethod
    def to_dto(cls, model_object: ModelObject) -> DtoObject:
        """
        Converte um objeto do modelo para um objeto DTO.

        O objetivo desse método é copiar todos os campos do modelo em questão
        para seus respectivos campos do DTO.
        """
        raise NotImplementedError

    @classmethod
    def all_to_model(cls, dto_objects: List[DtoObject]) -> List[ModelObject]:
        return list(map(cls.to_model, dto_objects))

    @classmethod
    def all_to_dto(cls, model_objects: List[ModelObject]) -> List[DtoObject]:
        return list(map(cls.to_dto, model_objects))
