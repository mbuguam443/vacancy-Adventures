from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import BlogPost, BlogCategory

def blog_list(request):
    posts_list = BlogPost.objects.filter(status='published').order_by('-created_at')
    category_slug = request.GET.get('category')

    if category_slug:
        posts_list = posts_list.filter(category__slug=category_slug)

    paginator = Paginator(posts_list, 6)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    categories = BlogCategory.objects.all()
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'categories': categories,
        'current_category': category_slug,
    })

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    recent_posts = BlogPost.objects.filter(status='published').exclude(id=post.id)[:3]
    categories = BlogCategory.objects.all()
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'recent_posts': recent_posts,
        'categories': categories,
    })
