'''
Created on Mar 16, 2018

@author: marcel.zoll
'''

def topoSort_gen(clist,
            attrib_lambda = lambda e: e.name,
            deplist_lambda = lambda e: e.dep):
    """ (Generator) Topologically sort a list of elements for their inner dependencies.
    From a list of elements with attributed name and dependency, generate a hierarchy sorted list where
    the dependencies of later emitted elements are met through the previously emitted
    
    Parameters
    ----------
    clist : list of objects
        some list of objects in which each elements has a defined name and dependency to other elements in the list
    attrib_lambda : lambda function
        a function applied to each element of the list returning its name
    deplist : lambda function
        a function applied to each element of the list returning a list of names of other elements that this element itself is dependent of
        
    Returns
    -------
    topologically sorted list where the elements' dependency is met by the previously emitted elements
    
    Example
    -------
    ```
        class A:
            name = 'A'
            dep = []
        class B:
            name = 'B'
            dep = ['A']
        list( topoSort_gen([B(),A()]) )
        >>> [class A, class B]
    ```
    """
    provided = set()
    while clist:
        remaining_clist = []
        emitted = False

        for cl in clist:
            item_name = attrib_lambda(cl)
            dependencies = set(deplist_lambda(cl))
            
            if dependencies.issubset(provided):
                yield cl
                provided.add(item_name)
                emitted = True
            else:
                remaining_clist.append( cl )

        if not emitted:
            raise Exception("TopologicalSortFailure")

        clist = remaining_clist


def list_of_uniques(obj_list, key_lambda = lambda e: e):
    """ generate the set of unique elements by a certain key, emit elements in the beginning of list with precidence """
    _ = set()
    return [obj for obj in obj_list if key_lambda(obj) not in _ and not _.add(key_lambda(obj)) ]

def list_of_uniquelistelements(obj_list, key_lambda = lambda e: e):
    """ get the objects which hold lists of unqiue occuring elements.
    Items are only guarantied to be unique in the sense of that the union of elements is identical before and after the sort """
    _ = []
    return [obj for obj in obj_list if (any([key not in _ for key in key_lambda(obj)])) and (not _.extend(key_lambda(obj))) ]
