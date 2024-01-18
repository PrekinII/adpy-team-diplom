from functools import wraps
from itertools import count


def api_slicer_decorator(api_method_name, method_val_name="owner_id", sub_dict="items"):
    def decorator(inner_func):
        @wraps(inner_func)
        def wrapper(self, *args, **kwargs):
            api_data_length = self.api_slicer(
                api_method_name, method_val_name, *args, **kwargs
            )

            all_data = []
            for offset in range(1):  # count(0, api_data_length) - replace to get a full version
                data = inner_func(self, offset, *args, **kwargs)

                if not data[sub_dict]:
                    break

                all_data.extend(data[sub_dict])

            return all_data

        return wrapper

    return decorator
