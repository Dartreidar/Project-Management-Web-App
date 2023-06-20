from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Phase, ProjectMember, Unit, Task, TaskAssignment
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Sum
import json
from django.core import serializers
from django.utils import timezone
import string,random

#開発用初期画面
def welcome_view(request):
    return render(request, 'welcome.html')

#プロジェクト一覧表示機能
def project_list(request):
    if request.method == 'GET':
        search_option = request.GET.get('search')
        sort_option = request.GET.get('sort')

        projects = Project.objects.all()

        # 検索オプションが指定された場合は、プロジェクト名でフィルタリング
        if search_option:
            projects = projects.filter(project_name__icontains=search_option)

        # ソートオプションに基づいてプロジェクトを並び替え
        if sort_option == 'created':
            projects = projects.order_by('created_at')
        elif sort_option == 'updated':
            projects = projects.order_by('-updated_at')
        elif sort_option == 'name':
            projects = projects.order_by('project_name')

        project_data = []
        for project in projects:
            # 進捗の計算
            total_tasks = 0
            completed_tasks = 0
            for phase in project.phases.all():
                for unit in phase.units.all():
                    tasks = unit.tasks.all()
                    total_tasks += tasks.count()
                    completed_tasks += tasks.filter(is_completed_task=True).count()

            progress = 0
            if total_tasks > 0:
                progress = completed_tasks / total_tasks * 100

            project_info = {
                'project': project,
                'progress': progress,
                'deadline': project.dead_line,
                'priority': project.priority,
                'total_work_hours': total_tasks * 10,  # 1タスクあたり10時間と仮定
                'responsible': project.responsible,
                'project_kind': project.project_kind,
            }
            project_data.append(project_info)

        context = {
            'projects': project_data,
            'search_option': search_option,
            'sort_option': sort_option,
        }

        return render(request, 'project_list.html', context)

    return JsonResponse({'success': False, 'message': '無効なリクエストメソッドです。'})

#プロジェクト削除機能
@csrf_exempt
def delete_project(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id)
            project.delete()
            return JsonResponse({'success': True})
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'プロジェクトが存在しません。'})
    
    return JsonResponse({'success': False, 'message': '無効なリクエストメソッドです。'})

@login_required
def project_join(request):
    invitation_id = request.GET.get('invitation_id')  # これでinvitation_idを取得
    if request.method == 'POST' and invitation_id is not None:
        project = Project.objects.filter(invitation_id=invitation_id).first()
        if project is not None:
            ProjectMember.objects.create(user=request.user, project=project, role='member')
        return redirect('project_list')
        
    elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if invitation_id is not None:
            project = Project.objects.filter(invitation_id=invitation_id).first()
            if project is not None:
                return JsonResponse({'project': {
                    'name': project.project_name,
                    'responsible': project.responsible.username
                }})
            else:
                return JsonResponse({'project': None})
        else:
            return JsonResponse({'error': 'No invitation ID provided'}, status=400)
    else:
        return render(request, 'project_join.html')


@login_required
def project_create(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        project_kind = request.POST.get('project_kind')
        project_deadline = request.POST.get('project_deadline')
        project_priority = request.POST.get('project_priority')
        project_status = request.POST.get('project_status')

        # ランダムな招待IDを生成
        invitation_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # プロジェクトをデータベースに保存
        project = Project.objects.create(
            project_name=project_name,
            project_description=project_description,
            project_kind=project_kind,
            responsible=request.user,  # プロジェクト作成者が初期の参加メンバー兼責任者
            priority=project_priority,
            invitation_id=invitation_id,
            dead_line=project_deadline
        )

        # プロジェクト作成者をメンバーとして追加
        ProjectMember.objects.create(
            user=request.user,
            project=project,
            role='manager'
        )

        return redirect('project_list')  # 作成後にプロジェクト一覧ページにリダイレクト

    return render(request, 'project_create.html')

#プロジェクト編集機能
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_description = request.POST.get('project_description')
        project_deadline = request.POST.get('project_deadline')
        project_priority = request.POST.get('project_priority')

        if project_name:  # Update only if new data is provided
            project.project_name = project_name

        if project_description:  # Update only if new data is provided
            project.project_description = project_description

        if project_deadline:  # Update only if new data is provided
            project.dead_line = project_deadline

        if project_priority:  # Update only if new data is provided
            project.priority = project_priority

        # Save updates to the database
        project.save()

        return redirect('project_list')

    context = {
        'project': project,
    }
    return render(request, 'project_edit.html', context)

#フェーズ一覧表示機能
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    phases = project.phases.order_by('dead_line')

    context = {
        'project': project,
        'phases': phases,
    }
    return render(request, 'project_detail.html', context)

#フェーズ作成機能（未完成）
def phase_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        phase_name = request.POST['phase_name']
        phase_description = request.POST['phase_description']
        phase_deadline = request.POST['phase_deadline']
        start_day = date.today()  #要修正、入力された日付を取得

        phase = Phase.objects.create(
            project=project,
            phase_name=phase_name,  # フィールド名を修正
            phase_description=phase_description,  # フィールド名を修正
            start_day=start_day,  # start_dayの値を設定
            dead_line=phase_deadline  # フィールド名を修正
        )

        #プロジェクト詳細画面にリダイレクト
        return redirect('project_detail', project_id=project_id)
        # Handle further actions or redirects

    context = {
        'project': project
    }

    return render(request, 'phase_create.html', context)

#フェーズ編集機能
def phase_edit(request, project_id, phase_id):
    phase = get_object_or_404(Phase, id=phase_id)

    if request.method == 'POST':
        phase_name = request.POST['phase_name']
        phase_description = request.POST['phase_description']
        phase_deadline = request.POST['phase_deadline']

        phase.phase_name = phase_name
        phase.phase_description = phase_description
        phase.dead_line = phase_deadline
        phase.save()

        return redirect('phase_detail', project_id=project_id, phase_id=phase_id)

    context = {
        'phase': phase
    }

    return render(request, 'phase_edit.html', context)

#ユニット一覧表示機能
def phase_detail(request, project_id, phase_id):
    phase = get_object_or_404(Phase, id=phase_id)
    project = phase.project
    return render(request, 'phase_detail.html', {'phase': phase, 'project': project})

def unit_create(request, project_id, phase_id):
    phase = get_object_or_404(Phase, pk=phase_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        unit_name = request.POST['unit_name']
        unit_description = request.POST['unit_description']
        unit_deadline = request.POST['unit_deadline']
        start_day = date.today()

        unit = Unit.objects.create(
            phase=phase,
            unit_name=unit_name,
            unit_description=unit_description,
            dead_line=unit_deadline,
            start_day=start_day
        )

        i = 1
        while True:
            task_name = request.POST.get(f'task_name_{i}')
            task_description = request.POST.get(f'task_description_{i}')
            task_deadline = request.POST.get(f'task_deadline_{i}')
            start_day = date.today()

            if not task_name and not task_description and not task_deadline:
                break

            if task_name:  # Only create task if name is present
                Task.objects.create(
                    unit=unit,
                    task_name=task_name,
                    task_description=task_description,
                    dead_line=task_deadline,
                    start_day=start_day
                )
            i += 1

        return redirect('phase_detail', project_id=project_id, phase_id=phase_id)
    return render(request, 'projectManagement/unit_create.html', {
        'project_id': project_id,
        'phase_id': phase_id,
    })


    task_range = range(1, 6)  # Adjust the range as per the maximum number of tasks

    context = {
        'phase': phase,
        'task_range': task_range
    }

    return render(request, 'unit_create.html', context)

#ユニット編集機能
def unit_edit(request, project_id, phase_id, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)

    if request.method == 'POST':
        unit_name = request.POST['unit_name']
        unit_description = request.POST['unit_description']
        unit_deadline = request.POST['unit_deadline']

        unit.unit_name = unit_name
        unit.unit_description = unit_description
        unit.deadline = unit_deadline
        unit.save()

        return redirect('phase_detail', project_id=project_id, phase_id=phase_id)

    context = {
        'unit': unit
    }

    return render(request, 'unit_edit.html', context)

#タスク詳細表示機能
def task_detail(request, project_id, phase_id, unit_id, task_id):
    task = get_object_or_404(Task, id=task_id)

    context = {
        'project_id': project_id,
        'phase_id': phase_id,
        'unit_id': unit_id,
        'task': task
    }

    return render(request, 'task_detail.html', context)

#タスク作成機能
def task_create(request, project_id, phase_id, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    project_members = ProjectMember.objects.filter(project_id=project_id)

    if request.method == 'POST':
        task_name = request.POST['task_name']
        task_description = request.POST['task_description']
        task_deadline = request.POST['task_deadline']
        task_member_id = request.POST['task_member']

        task = Task.objects.create(
            task_name=task_name,
            task_description=task_description,
            unit=unit,
            start_day=date.today(),
            dead_line=task_deadline
        )

        task_assignment = TaskAssignment.objects.create(
            task=task,
            project_member_id=task_member_id
        )

        return redirect('task_detail', project_id=project_id, phase_id=phase_id, unit_id=unit_id, task_id=task.id)


#タスク編集機能(未完成)
def task_edit(request):
    return render(request, 'task_edit.html')
