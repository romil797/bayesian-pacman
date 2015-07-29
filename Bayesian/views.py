from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import numpy as np
import base64
import json

#region serializer
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        if input object is a ndarray it will be converted into a dict holding dtype, shape and the data base64 encoded
        """
        if isinstance(obj, np.ndarray):
            data_b64 = base64.b64encode(obj.data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder(self, obj)


def json_numpy_obj_hook(dct):
    """
    Decodes a previously encoded numpy ndarray
    with proper shape and dtype
    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct
#endregion end serializer

# ASSUMES that the matrix is a square matrix
def sample_treasure(tMat):
    n = len(tMat)
    r = np.random.uniform()
    for i in xrange(n):
        for j in xrange(n):
            r -= tMat[i][j]
            
            if r <= 0:
                location = (i, j)
                return location

def game(request):
    t = get_template('game.html')
    n = 4
    # Initialize tMat if not already created
    if 'tMat' not in request.session:
        tMat = np.random.rand(n,n)
        sum = np.sum(tMat)
        tMat = tMat/sum
    else:
        input_mat = json.loads(request.session['tMat'], object_hook=json_numpy_obj_hook)
        tMat = np.random.rand(n,n)
        for i in xrange(n):
            for j in xrange(n):
                tMat[i][j] = input_mat[i][j]
        
    if 'dMat' not in request.session:
        dMat = np.random.rand(n,n)
    else:
        input_mat = json.loads(request.session['dMat'], object_hook=json_numpy_obj_hook)
        dMat = np.random.rand(n,n)
        for i in xrange(n):
            for j in xrange(n):
                dMat[i][j] = input_mat[i][j]
                
    # Sample the treasure if necessary.
    if 'location' not in request.session:
        location = sample_treasure(tMat)
        request.session['location'] = str(location[0]) + ',' + str(location[1])
    else:    
        location = tuple(request.session['location'].split(','))
        
    # DO STUFF WITH tMat IF NECESSARY
    for i in xrange(n):
        for j in xrange(n):
            if request.GET.get(str(i)+','+str(j)):
                # Check to see if we found the treasure
                if int(location[0]) == i and int(location[1]) == j:
                    tMat = tMat * 0.
                    tMat[i][j] = 1.
                else:
                    tMat[i][j] = 0.
                    sum = np.sum(tMat)
                    tMat = tMat/sum
                    
                break
            
    mMat = np.multiply(tMat, dMat)

    request.session['tMat'] = json.dumps(tMat, cls=NumpyEncoder)
    request.session['dMat'] = json.dumps(dMat, cls=NumpyEncoder)

    
    html = t.render(Context({'tMat': tMat, 'dMat': dMat, 'mMat': mMat, 'location': location}))
    
    return HttpResponse(html)
    

