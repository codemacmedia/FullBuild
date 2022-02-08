from unicodedata import category
from django.shortcuts import render
#from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from base.models import Product, Review
from base.serializers import ProductSerializer
# Create your views here.

from rest_framework import status


@api_view(['GET'])
def getProducts(request):
    
    query = request.query_params.get('keyword')
    if query == None:
        query = ''
        
    products = Product.objects.filter(name__icontains=query)
    
    ## Get the page number we should be on 
    page = request.query_params.get('page')
    ## Paginator takes in the query-set (products) for pagination
    paginator = Paginator(products,5)
    
    
    try:
        # paginate a page(current page)
        products = paginator.page(page)
    except PageNotAnInteger:
        # return first page
        products = paginator.page(1)
    except EmptyPage:
        #return the last page ex. 1-10 returns 10
        products = paginator.page(paginator.num_pages)
    
    #If page is equal to None default to page 1. Casting page as int.
    if page == None:
        page = 1
    page = int(page)
    
    serializer = ProductSerializer(products, many=True)
    ## returning product, a page and number of pages
    return Response({'products':serializer.data, 'page':page, 'pages': paginator.num_pages})

@api_view(['GET'])
def getTopProducts(request):
    #taing greater then 4 order by highest first 
    products = Product.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    user = request.user
    
    product = Product.objects.create(
        user = user,
        name='Sample Name',
        price=0,
        brand='Sample Brand',
        countInStock=0,
        category='Sample Category',
        description=''
    )
    
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    data = request.data
    product = Product.objects.get(_id=pk)
    
    product.name = data['name']
    product.price = data['price']
    product.brand = data['brand']
    product.countInStock = data['countInStock']
    product.category = data['category']
    product.description = data['description']
        
    product.save()
    
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)



@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    product = Product.objects.get(_id=pk)
    product.delete()
    return Response('Product Deleted')


@api_view(['POST'])
def uploadImage(request):
    data = request.data
    #Get product by it's id
    product_id = data['product_id']
    product = Product.objects.get(_id=product_id)
    
    ## Send a get request to files and get image as a string & set the select image to products (image field) product.image
    product.image = request.FILES.get('image')
    ## save to product
    product.save()
    
    return Response('Image was uploaded')

## Takes in request and pk. Will be passed into url parms so we can see which 
## product we want to review. POST request and user must be authenicated.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    #Get user from token 
    user = request.user
    #Get product objects from Product Model 
    product = Product.objects.get(_id=pk)
    data=request.data
    
    #1 - Review already exists - If a Customer wrote a review already
  
    #Querying all the product reviews, if user exists with this value for this product add in exists(return t or f value)
    alreadyExists = product.review_set.filter(user=user).exists()
    if alreadyExists:
        content = {'detail':'Product already reviewed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #2 else if No Rate or 0
    # Inform customer they need to submit rating
    elif data['rating'] == 0:
        content = {'detail':'Please select a rating'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #3 - Create Review 
    #If the form data checks-out perform calulations and submit it 
    else:
        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment'],     
        )
        reviews = product.review_set.all()
        # Check number of reviews the product has
        product.numReviews = len(reviews)
        
        total = 0
        for i in reviews:
            total += i.rating
            #rating = total/ number of reviews
            product.rating = total / len(reviews)
            product.save()
            
            return Response('Review Added')
        
    
    
    
    
    
    
    
    