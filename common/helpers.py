class ModelModifer:
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
