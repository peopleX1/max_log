from django.db import models


STEP_LABELS = {
    'connecting': 'Подключение',
    'phone_entry': 'Ввод номера',
    'waiting': 'Ожидание',
    'captcha': 'Проверка капчи',
    'code': 'Ввод кода',
    'error': 'Ошибка',
}


class Visitor(models.Model):
    visitor_id = models.CharField(max_length=64, unique=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=64, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    step = models.CharField(max_length=32, blank=True)
    needs_action = models.BooleanField(default=False)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Посетитель"
        verbose_name_plural = "Посетители"

    def __str__(self) -> str:
        return self.phone or self.visitor_id


class VisitorLogEntry(models.Model):
    visitor = models.ForeignKey(Visitor, related_name='log_entries', on_delete=models.CASCADE)
    field = models.CharField(max_length=32)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись лога"
        verbose_name_plural = "Записи лога"
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'{self.visitor}: {self.field}={self.value}'
