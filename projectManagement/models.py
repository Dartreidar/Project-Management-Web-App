from django.db import models
from django.contrib.auth.models import AbstractUser


class Project(models.Model):
    name = models.CharField(max_length=255)  # プロジェクト名
    description = models.TextField()  # プロジェクトの説明
    deadline = models.DateTimeField()  # プロジェクトの締め切り日時
    members = models.ManyToManyField(  # プロジェクトメンバー
        AbstractUser,
        through='ProjectMember',
        related_name='projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    class Meta:
        ordering = ['-created_at']  # 作成日時の降順でソート


class ProjectMember(models.Model):
    PROJECT_ROLE_CHOICES = [  # プロジェクトメンバーの役割の選択肢
        ('manager', 'Manager'),  # マネージャー
        ('worker', 'Worker'),  # ワーカー
        ('stakeholder', 'Stakeholder'),  # ステークホルダー
    ]
    user = models.ForeignKey(  # プロジェクトメンバーのユーザー
        AbstractUser,
        on_delete=models.CASCADE,
        related_name='project_memberships',
    )
    project = models.ForeignKey(  # 所属するプロジェクト
        Project,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.CharField(  # 役割
        max_length=20,
        choices=PROJECT_ROLE_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    class Meta:
        unique_together = ('user', 'project')  # ユーザーとプロジェクトの組み合わせが一意


class Phase(models.Model):
    name = models.CharField(max_length=255)  # フェーズ名
    description = models.TextField()  # フェーズの説明
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases',
    )  # フェーズが所属するプロジェクト
    start_date = models.DateTimeField()  # フェーズの開始日時
    end_date = models.DateTimeField()  # フェーズの終了日時
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    class Meta:
        ordering = ['-start_date']  # 開始日時の降順でソート


class Unit(models.Model):
    name = models.CharField(max_length=255)  # ユニット名
    description = models.TextField()  # ユニットの説明
    deadline = models.DateTimeField()  # ユニットの締め切り日時
    phase = models.ForeignKey(  # ユニットが所属するフェーズ
        Phase,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時


class Task(models.Model):
    name = models.CharField(max_length=255)  # タスク名
    description = models.TextField()  # タスクの説明
    deadline = models.DateTimeField()  # タスクの締め切り日時
    unit = models.ForeignKey(  # タスクが所属するユニット
        Unit,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時
    assigned_users = models.ManyToManyField(  # タスクに割り当てられたユーザー
        AbstractUser,
        through='TaskAssignment',
        related_name='task_assignments',
    )

    def is_completed(self):
        if not hasattr(self, '_is_completed'):
            # `_is_completed` 属性が存在しない場合の処理
            self._is_completed = all(
                task_assignment.is_completed
                for task_assignment in self.taskassignment_set.all()
            )
            # タスクに関連する全ての TaskAssignment の完了状態をチェックし、
            # その結果を `_is_completed` 属性に格納する
        return self._is_completed
        # `_is_completed` 属性の値を返す



class TaskAssignment(models.Model):
    task = models.ForeignKey(  # 割り当てられたタスク
        Task,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(  # 割り当てられたユーザー
        AbstractUser,
        on_delete=models.CASCADE,
        related_name='task_assignments',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)  # 割り当て日時
    is_completed = models.BooleanField(default=False)  # タスクが完了したかどうか

    class Meta:
        unique_together = ('task', 'user',)  # タスクとユーザーの組み合わせは一意

    def complete(self):
        self.is_completed = True  # タスクを完了済みに設定
        self.save()
        if self.task.is_completed():  # タスクが完了した場合
            # タスクが完了した場合の処理
            pass

