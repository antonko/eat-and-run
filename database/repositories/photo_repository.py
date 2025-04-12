import gel

from database.models.photos import PhotoModel


class PhotoRepository:
    """Репозиторий для работы с фотографиями."""

    def __init__(self, executor: gel.AsyncIOExecutor) -> None:
        """Инициализация репозитория."""
        self.executor = executor

    async def save_photo(self, photo: PhotoModel) -> PhotoModel:
        """Сохранить фотографию."""
        query = """
        with
            file_data_base64 := <str>$file_data_base64,
            file_name := <str>$file_name,
            mime_type := <str>$mime_type,
            description := <optional str>$description,
            user_id := <optional uuid>$user_id
        select (
            insert Photo {
                file_data_base64 := file_data_base64,
                file_name := file_name,
                mime_type := mime_type,
                description := description,
                user := (select User filter .id = user_id)
            }
        )
        {
            id,
            id_int,
            file_data_base64,
            file_name,
            mime_type,
            created_at,
            description,
            user: {
                id
            }
        }
        """

        result = await self.executor.query_single_json(
            query,
            file_data_base64=photo.file_data_base64,
            file_name=photo.file_name,
            mime_type=photo.mime_type,
            description=photo.description,
            user_id=photo.user_id,
        )

        return PhotoModel.model_validate_json(result, strict=False)

    async def get_photo_by_id_int(self, id_int: int) -> PhotoModel | None:
        """Получить фотографию по целочисленному идентификатору."""
        query = """
        select Photo {
            id,
            id_int,
            file_data_base64,
            file_name,
            mime_type,
            created_at,
            description,
            user: {
                id
            }
        }
        filter .id_int = <int64>$id_int
        """

        result = await self.executor.query_single_json(query, id_int=id_int)

        if result is None or result == "null":
            return None

        return PhotoModel.model_validate_json(result, strict=False)
