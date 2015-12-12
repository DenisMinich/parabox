class WidgetsCollection(list):
    def __init__(self, objects, parent_widget):
        super(WidgetsCollection, self).__init__(objects)
        self.parent_widget = parent_widget
        self.parent_widget.bind(on_update=self.update)
        for new_object in objects:
            self.parent_widget.add_widget(new_object)

    def append(self, new_object):
        super(WidgetsCollection, self).append(new_object)
        self.parent_widget.add_widget(new_object)

    def insert(self, index, new_object):
        super(WidgetsCollection, self).insert(index, new_object)
        self.parent_widget.add_widget(new_object)

    def pop(self, index):
        result = super(WidgetsCollection, self).pop(index)
        self.parent_widget.remove_widget(result)
        return result

    def remove(self, object_to_remove):
        super(WidgetsCollection, self).remove(object_to_remove)
        self.parent_widget.remove_widget(object_to_remove)

    def clear(self):
        for widget_to_delete in self:
            self.parent_widget.remove_widget(widget_to_delete)
        super(WidgetsCollection, self).clear()

    def extend(self, iterable):
        super(WidgetsCollection, self).extend(iterable)
        for new_object in iterable:
            self.parent_widget.add_widget(new_object)

    def update(self, *args, **kwargs):
        for world_object in self:
            world_object.update(*args, **kwargs)

