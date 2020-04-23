from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    """Домашняя страница приложения Learning Logs"""
    return render(request, 'index.html')


@login_required
def topics(request):
    """Выводит список тем"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'topics.html', context)


@login_required
def topic(request, topic_id):
    """Выводит одну тему и все её записи"""
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(topic, request)

    entries = topic.entry_set.order_by('-date_added')
    for entry in entries:
        print(entry.date_added)
    context = {'topic': topic, 'entries': entries}
    return render(request, 'topic.html', context)


@login_required
def new_topic(request):
    """Определяет новую тему"""
    if request.method != 'POST':
        # Данные не отправились, создается пустая форма
        form = TopicForm()
    else:
        # Отправляем данные POST; Обрабатываем данные
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {'form': form}
    return render(request, 'new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic = get_object_or_404(Topic, id=topic_id)
    check_topic_owner(topic, request)
    if request.method != 'POST':
        # Данные не отправились, создаётся пустая форма
        form = EntryForm()
    else:
        # Отправляем данные POST, обрабатываем данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',
                                                args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Редактирует сущетсвующую запись"""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    check_topic_owner(topic, request)

    if request.method != 'POST':
        # Исходный запрос, форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST, обработать данные
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',
                                                args=[topic.id]))

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'edit_entry.html', context)


def check_topic_owner(topic, request):
    if topic.owner != request.user:
        raise Http404
