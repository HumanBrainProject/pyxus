class MergeUtils(object):

    def merge(self, origin_instance, target_instance, list_of_references):
        for key in origin_instance.data:
            self.__add_if_not_exists(origin_instance.data, target_instance.data, key)
        self.__merge_key(origin_instance.data, target_instance.data, "http://schema.org/identifier")
        for ref_instance in [list_of_references]:
            self.__update_reference(ref_instance.data, "a", "b")

    def __update_reference(self, referring_instance, old_link, new_link, parent_key=None):
        if type(referring_instance) is list:
            for el in referring_instance:
                self.__update_reference(el, old_link, new_link)
        elif type(referring_instance) is dict:
            for key in referring_instance:
                result = self.__update_reference(referring_instance[key], old_link, new_link, key)
                if result is not None:
                    referring_instance[key] = result
        elif parent_key is not None and parent_key=="@id" and referring_instance==old_link:
            return new_link
        else:
            return None

    def __add_if_not_exists(self, origin, target, key):
        if key not in target:
            target[key] = origin[key]

    def __merge_key(self, origin, target, key):
        if key in target:
            if type(target[key]) is not list:
                new_list = list()
                new_list.append(target[key])
                target[key] = new_list
            if type(origin[key]) is list:
                for el in origin[key]:
                    target[key].append(el)
            else:
                target[key].append(origin[key])
        else:
            target[key] = origin[key]
