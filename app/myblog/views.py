# -*- coding: utf-8 -*-
import math

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage
import markdown

from app.utils import *
from app.myblog.models import *
from app.decorater import api_times

# Create your views here.


# def not_found(req):
#     return render_to_response("404.html", status_code=404)
#
#
# def server_error(req):
#     return render_to_response("500.html", status_code=500)


@ensure_csrf_cookie
def index(req):
    return render_to_response('index.html')



def blog(req, bid=None):
    if bid is not None:
        if bid == '#':
            return render_to_response('blog_detail.html')
        blog = get_object_or_404(Article, id=bid)
        return render_to_response('blog_detail.html')
    return render_to_response('blog.html')


def classify(req, bid=None):
    return render_to_response("blog.html")


def tag(req, bid=None):
    return render_to_response("blog.html")


def know(req):
    return render_to_response('knowledge.html')

@api_times
def get_classify(req, cid=None):
    body={}
    blog_list = Article.objects.filter(publish=True, classification__id=cid).order_by('-create_time')
    total = blog_list.count()
    total_page = math.ceil(float(total) / 4.0)
    paginator = Paginator(blog_list, 4)
    page_num = 1
    try:
        page_num = int(req.GET.get('page'))
        blog_list = paginator.page(page_num)
    except PageNotAnInteger:
        blog_list = paginator.page(1)
    except EmptyPage:
        blog_list = []
    except:
        blog_list = paginator.page(page_num)
    blog_json = model_serializer(blog_list, serializer='dict', datetime_format='string')
    for i, itm in enumerate(blog_list):
        # blog_json[i]['content'] = gfm.markdown(gfm.gfm(itm.content[:400]))
        blog_json[i]['content'] = markdown.markdown(itm.content[:400], ['codehilite'])
        blog_json[i]['classify'] = model_serializer(itm.classification, include_attr=['c_name', 'id'])
        blog_json[i]['tags'] = model_serializer(itm.tags.all(), include_attr=['tag_name', 'id'])
    page_list = []
    for i in range(1, int(total_page) + 1):
        paged={}
        paged['page'] = i
        if i == page_num:
            paged['active'] = True
        else:
            paged['active'] = False
        page_list.append(copy.copy(paged))
    if page_num == total_page:
        nextp = 0
        prep = total_page - 1
    elif page_num == 1:
        prep = 0
        nextp = page_num + 1
    else:
        prep = page_num - 1
        nextp = page_num + 1
    if page_num > total_page:
        prep = total_page
        nextp = 0
    pagination = {'page': page_num,
                  'total_page': total_page,
                  'total': total,
                  'pre': prep,
                  'next': nextp,
                  'page_list': page_list}
    body['blog_list'] = blog_json
    body['pagination'] = pagination
    return HttpResponse(encodejson(1, body), content_type="application/json")


@api_times
def get_tag(req, tid=None):
    body={}
    blog_list = Article.objects.filter(publish=True, tags__id=tid).order_by('-create_time')
    total = blog_list.count()
    total_page = math.ceil(float(total) / 4.0)
    paginator = Paginator(blog_list, 4)
    page_num = 1
    try:
        page_num = int(req.GET.get('page'))
        blog_list = paginator.page(page_num)
    except PageNotAnInteger:
        blog_list = paginator.page(1)
    except EmptyPage:
        blog_list = []
    except:
        blog_list = paginator.page(page_num)
    blog_json = model_serializer(blog_list, serializer='dict', datetime_format='string')
    for i, itm in enumerate(blog_list):
        # blog_json[i]['content'] = gfm.markdown(gfm.gfm(itm.content[:400]))
        blog_json[i]['content'] = markdown.markdown(itm.content[:400], ['codehilite'])
        blog_json[i]['classify'] = model_serializer(itm.classification, include_attr=['c_name', 'id'])
        blog_json[i]['tags'] = model_serializer(itm.tags.all(), include_attr=['tag_name', 'id'])
    page_list = []
    for i in range(1, int(total_page) + 1):
        paged={}
        paged['page'] = i
        if i == page_num:
            paged['active'] = True
        else:
            paged['active'] = False
        page_list.append(copy.copy(paged))
    if page_num == total_page:
        nextp = 0
        prep = total_page - 1
    elif page_num == 1:
        prep = 0
        nextp = page_num + 1
    else:
        prep = page_num - 1
        nextp = page_num + 1
    if page_num > total_page:
        prep = total_page
        nextp = 0
    pagination = {'page': page_num,
                  'total_page': total_page,
                  'total': total,
                  'pre': prep,
                  'next': nextp,
                  'page_list': page_list}
    body['blog_list'] = blog_json
    body['pagination'] = pagination
    return HttpResponse(encodejson(1, body), content_type="application/json")



@api_times
def detail(req, bid):
    body={}
    blog_list = Article.objects.filter(id=bid, publish=True)
    all_blog = Article.objects.all().order_by('create_time')
    if not blog_list.exists():
        body['blog'] = ''
        return HttpResponse(encodejson(7, body), content_type='application/json')
    blog = blog_list[0]
    blog.read_count += 1
    blog.save()
    preb = '#'
    nextb = '#'
    pre_title = ''
    next_title = ''
    # print len(all_blog)
    for i, itm in enumerate(all_blog):
        if itm == blog:
            if i == 0:
                preb = itm.id
                pre_title = ''
            else:
                preb = all_blog[i-1].id
                pre_title = all_blog[i-1].caption
            if (i+1) == all_blog.count():
                nextb = itm.id
                next_title = ''
            else:
                nextb = all_blog[i+1].id
                next_title = all_blog[i+1].caption
            break

    pagination = {'pre_id': preb,
                  'next_id': nextb,
                  'pre_title': pre_title,
                  'next_title': next_title}
    comment_list_json = []
    comment_list = Comment.objects.filter(belong=blog).order_by("-create_time")
    have_comment = False
    if comment_list.exists():
        have_comment = True
        for itm in comment_list:
            comment_json = model_serializer(itm, datetime_format="string")
            comment_json['have_reply'] = False
            if itm.reply is True:
                comment_reply = itm.replys.all().order_by('create_time')
                reply_json = model_serializer(comment_reply, datetime_format="string")
                comment_json['have_reply'] = True
                comment_json['reply'] = reply_json
            comment_list_json.append(copy.copy(comment_json))
    blog.content = markdown.markdown(blog.content, ['codehilite'])
    blog_json = model_serializer(blog, deep=True, datetime_format="string")
    blog_json['tags'] = model_serializer(blog.tags.all())
    verify, code = create_verify_code()
    req.session['verify'] = code.upper()
    body['verify'] = verify
    body['blog'] = blog_json
    body['comment'] = comment_list_json
    body['have_comment'] = have_comment
    body['pagination'] = pagination
    return HttpResponse(encodejson(1, body), content_type='application/json')


@api_times
def get_blog(req):
    body={}
    blog_list = Article.objects.filter(publish=True).order_by('-create_time')
    total = blog_list.count()
    total_page = math.ceil(float(total) / 4.0)
    paginator = Paginator(blog_list, 4)
    page_num = 1
    try:
        page_num = int(req.GET.get('page'))
        blog_list = paginator.page(page_num)
    except PageNotAnInteger:
        blog_list = paginator.page(1)
    except EmptyPage:
        blog_list = []
    except:
        blog_list = paginator.page(page_num)
    blog_json = model_serializer(blog_list, serializer='dict', datetime_format='string')
    for i, itm in enumerate(blog_list):
        # blog_json[i]['content'] = gfm.markdown(gfm.gfm(itm.content[:400]))
        blog_json[i]['content'] = markdown.markdown(itm.content[:400], ['codehilite'])
        blog_json[i]['classify'] = model_serializer(itm.classification, include_attr=['c_name', 'id'])
        blog_json[i]['tags'] = model_serializer(itm.tags.all(), include_attr=['tag_name', 'id'])
    page_list = []
    for i in range(1, int(total_page) + 1):
        paged={}
        paged['page'] = i
        if i == page_num:
            paged['active'] = True
        else:
            paged['active'] = False
        page_list.append(copy.copy(paged))
    if page_num == total_page:
        nextp = 0
        prep = total_page - 1
    elif page_num == 1:
        prep = 0
        nextp = page_num + 1
    else:
        prep = page_num - 1
        nextp = page_num + 1
    pagination = {'page': page_num,
                  'total_page': total_page,
                  'total': total,
                  'pre': prep,
                  'next': nextp,
                  'page_list': page_list}
    body['blog_list'] = blog_json
    body['pagination'] = pagination
    return HttpResponse(encodejson(1, body), content_type="application/json")


def get_tools(req):
    body={}
    latest_list = Article.objects.filter(publish=True).order_by('-create_time')
    if latest_list.count() > 5:
        latest_list = latest_list[0:5]
    classify_list = Classification.objects.all().order_by('-create_time')
    read_list = Article.objects.filter(publish=True).order_by('-read_count')
    if read_list.count() > 5:
        read_list = read_list[0:4]
    latest_json = model_serializer(latest_list, include_attr=['caption', 'create_time', 'id'], datetime_format="string")
    classify_json = model_serializer(classify_list, include_attr=['c_name', 'id'])
    read_json = model_serializer(read_list, include_attr=['caption', 'read_count', 'id'])
    body['latest_list'] = latest_json
    body['classify_list'] = classify_json
    body['read_list'] = read_json
    return HttpResponse(encodejson(1, body), content_type='application/json')


@csrf_exempt
def submit_comment(req, bid=None):
    body={}
    filter_list = [u'rapospectre', u'Bloggers', u'Blog owner', u'Webmaster', u'Author', u'The author', u'Article author', u'author', u'blog master']
    if bid is None:
        body['fail_mes'] = 'id illegal'
        return HttpResponse(encodejson(7, body), content_type='application/json')
    verify = str(req.POST.get('verify')).upper()
    if verify != req.session.get('verify'):
        body['fail_mes'] = 'Verification code error'
        return HttpResponse(encodejson(12, body), content_type='application/json')
    content = req.POST.get('content')
    nick = req.POST.get('nick')
    # try:
    #     check = unicode(nick)
    #     check = check.lower()
    # except UnicodeEncodeError:
    #     pass
    if unicode(nick).lower() in filter_list:
        body['fail_mes'] = 'Do not write nickname yo ~ I have to take a small notebook to remember you!'
        return HttpResponse(encodejson(6, body), content_type='application/json')
    blog_list = Article.objects.filter(id=bid)
    if not blog_list.exists():
        body['fail_mes'] = 'id 不合法'
        return HttpResponse(encodejson(7, body), content_type='application/json')
    blog = blog_list[0]
    if nick == '' or nick is None:
        nick = 'Anonymous User'
    mid = req.POST.get('mid', None)
    user = req.session.get('user', None)
    if user == 'kovaljov':
        nick = 'Kovaljov'
        avatar = 'master.png'
    else:
        avatar = 'default.png'
    if mid is None:
        new_comment = Comment(content=content, author=nick, belong=blog, avatar=avatar)
        new_comment.save()
    else:
        tid = req.POST.get('tid', None)
        to_the = req.POST.get('to', None)
        cmmnt = Comment.objects.filter(id=mid)
        if cmmnt.exists():
            cmmnt = cmmnt[0]
            cmmnt.reply = True
            new_reply = CommentReply(replyed=cmmnt,
                                     author=nick,
                                     content=content,
                                     to=to_the,
                                     avatar=avatar)
            new_reply.save()
            cmmnt.save()
    blog.comment_count += 1
    blog.save()
    # print new_comment.content
    return HttpResponse(encodejson(1, body), content_type='application/json')


def refresh_verify(req):
    body={}
    verify, code = create_verify_code()
    req.session['verify'] = code.upper()
    body['verify'] = verify
    return HttpResponse(encodejson(1, body), content_type="application/json")


@api_times
def get_index(req):
    body={}
    blog_list = Article.objects.filter(publish=True).order_by('-create_time')
    all_blog = Article.objects.all().order_by('create_time')
    if not blog_list.exists():
        body['blog'] = ''
        return HttpResponse(encodejson(7, body), content_type='application/json')
    blog = blog_list[0]
    blog.read_count += 1
    blog.save()
    preb = '0'
    nextb = '0'
    pre_title = ''
    next_title = ''
    # print len(all_blog)
    for i, itm in enumerate(all_blog):
        if itm == blog:
            if i == 0:
                preb = itm.id
                pre_title = ''
            else:
                preb = all_blog[i-1].id
                pre_title = all_blog[i-1].caption
            if (i+1) == all_blog.count():
                nextb = itm.id
                next_title = ''
            else:
                nextb = all_blog[i+1].id
                next_title = all_blog[i+1].caption
            break

    pagination = {'pre_id': preb,
                  'next_id': nextb,
                  'pre_title': pre_title,
                  'next_title': next_title}
    blog.content = markdown.markdown(blog.content)
    blog_json = model_serializer(blog, deep=True, datetime_format="string")
    blog_json['tags'] = model_serializer(blog.tags.all())
    body['blog'] = blog_json
    body['pagination'] = pagination
    return HttpResponse(encodejson(1, body), content_type='application/json')


def migrate_blog(req):
    blog_list = Article.objects.all().order_by('-create_time')
    blog_json = model_serializer(blog_list, deep=True, datetime_format="string")
    return HttpResponse(encodejson(1, {'blog': blog_json}), content_type='application/json')


def migrate_knows(req):
    know_list = Knowledge.objects.all().order_by("-create_time")
    know_json = model_serializer(know_list, datetime_format='string')
    return HttpResponse(encodejson(1, {'knows': know_json}), content_type='application/json')
