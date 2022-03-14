import os
import framework.model.helpers

databases = {
    'mongo': ['framework.mongomodel','framework.mongomodel.BaseMongoModel', 'framework.mongomodel.MongoModel'],
    'elastic': ['framework.elasticmodel','framework.elasticmodel.BaseElasticModel', 'framework.elasticmodel.ElasticModel']    
}

def generate(m):
    fbase = os.path.splitext(os.path.basename(m._tx_model_params['file']))[0]
    db = databases[m._tx_model_params['db']]
    for model in m.models:
        model.dbbase = db
        model.fbase = fbase


    #1) Generate the enum's in a seperate file
    enumoutput = framework.model.helpers.EnumsFile(m.enums).render()
    fname = f'{fbase}_enum.py'
    with open(fname,"w") as f:
        f.write(enumoutput)

    #2) Generate the Model's in a seperate file
    # modeloutput = '\n'.join(list(map(lambda x: x.render(), m.models)))
    modeloutput = framework.model.helpers.ModelsFile(m.models).render()
    fname = f'{fbase}_model.py'
    with open(fname,"w") as f:
        f.write(modeloutput)

    #3) Generate the standard API endpoints in a seperate file
    # stdapioutput = '\n'.join(list(map(lambda x: framework.model.helpers.StdApi(x).render(), m.models)))
    stdapioutput = framework.model.helpers.StdApiFile(m.models).render()
    fname = f'{fbase}_stdapi.py'
    with open(fname,"w") as f:
        f.write(stdapioutput)

    #4) Generate the custom action's in their own files to make the editing easy
    for model in m.models:
        for action in model.actions:
            action.fbase = fbase
            actionfile = f'{model.name.lower()}_{action.name.lower()}.py'
            if not os.path.exists(actionfile):
                with open(actionfile,"w") as f:
                    f.write(action.render())

    #5) Create the db related items in seperate file
    modeloutput = '\n'.join(list(map(lambda x: x.render(), m.models)))
    fname = f'{fbase}_db.py'
    # with open(fname,"w") as f:
    #     f.write(modeloutput)

    

    

    

    # apioutput = '\n'.join(list(map(lambda x: x.render(), m.models)))
    # fname = f'{fbase}_api.py'
    # with open(fname,"w") as f:
    #     f.write(apioutput)

    # actionoutput = '\n'.join(list(map(lambda x: x.render(), m.models)))
    # fname = f'{fbase}_action.py'
    # with open(fname,"w") as f:
    #     f.write(actionoutput)
