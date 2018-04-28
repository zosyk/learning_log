# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Topic, Entry
from .forms import TopicForm, EntryForm


# Create your views here.

def index(request):
    """ The home page for learning log"""
    return render(request, 'learning_logs/index.html')


def topics(request):
    """ Show all topics"""
    user = request.user
    if user.is_authenticated:
        topics = Topic.objects.filter(owner=user).order_by('date_added')
    else:
        topics = Topic.objects.filter(public=True).order_by('date_added')

    context = {'topics': topics}

    return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
    """ Show a single topic and all its entries """
    topic = get_object_or_404(Topic, id=topic_id)

    validate_topic_rights(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}

    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()

            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {"form": form}

    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """ Add a new entry """
    topic = get_object_or_404(Topic, id=topic_id)

    validate_topic_rights(request, topic)

    if request.method != 'POST':
        # No data submitted; create a blank form
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()

            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic

    validate_topic_rights(request, topic)

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))

    context = {'form': form, 'entry': entry, 'topic': topic}
    return render(request, 'learning_logs/edit_entry.html', context)


def validate_topic_rights(request, topic):

    if topic.public:
        return

    # Make sure that topic belongs to the current user
    if topic.owner != request.user:
        raise Http404
