import importlib
import logging
logger = logging.getLogger(__name__)

def load_generator(module_path: str, class_name: str, base_class: type):
    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        if not issubclass(cls, base_class):
            logger.error(f"{class_name} не наследуется от {base_class.__name__}")
            return None
        return cls()
    except Exception as e:
        logger.error(f"Ошибка загрузки {module_path}.{class_name}: {e}")
        return None