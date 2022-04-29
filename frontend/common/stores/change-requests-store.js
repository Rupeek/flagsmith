const BaseStore = require('./base/_store');
const OrganisationStore = require('./organisation-store');
const data = require('../data/base/_data');
const { env } = require('../../.eslintrc');

const createdFirstFeature = false;
const controller = {

    actionChangeRequest: (id, action, cb) => {
        store.loading();
        data.post(`${Project.api}features/workflows/change-requests/${id}/${action}/`)
            .then((res) => {
                data.get(`${Project.api}features/workflows/change-requests/${id}/`)
                    .then((res) => {
                        store.model[id] = res;
                        cb && cb();
                        store.loaded();
                    });
            }).catch(e => API.ajaxHandler(store, e));
    },
    getChangeRequests: (envId, committed) => {
        store.loading();
        store.envId = envId;
        const endpoint = `${Project.api}environments/${envId}/list-change-requests/?include_committed=${1}`;
        data.get(endpoint)
            .then((res) => {
                const committed = [];
                const results = [];
                if (res) {
                    res.map((v) => {
                        if (v.committed_at) {
                            committed.push(v);
                        } else {
                            results.push(v);
                        }
                    });
                }
                if (flagsmith.hasFeature('scheduling')) {
                    store.committed[envId] = committed.filter(v => !v.live_from);
                    store.scheduled[envId] = committed.filter(v => !!v.live_from);
                } else {
                    store.committed[envId] = committed;
                }
                store.model[envId] = results;

                store.loaded();
            }).catch(e => API.ajaxHandler(store, e));
    },
    deleteChangeRequest: (id, cb) => {
        store.loading();
        data.delete(`${Project.api}features/workflows/change-requests/${id}/`)
            .then((res) => {
                store.loaded();
                cb();
            }).catch(e => API.ajaxHandler(store, e));
    },
    updateChangeRequest: (changeRequest) => {
        store.loading();
        data.put(`${Project.api}features/workflows/change-requests/${changeRequest.id}/`, changeRequest)
            .then((res) => {
                store.model[changeRequest.id] = res;
                store.loaded();
            }).catch(e => API.ajaxHandler(store, e));
    },
    getChangeRequest: (id) => {
        store.loading();
        data.get(`${Project.api}features/workflows/change-requests/${id}/`)
            .then((res) => {
                store.model[id] = res;
                store.loaded();
            }).catch(e => API.ajaxHandler(store, e));
    },
};


const store = Object.assign({}, BaseStore, {
    id: 'change-request-store',
    model: {},
    committed: {},
    scheduled: {},
});


store.dispatcherIndex = Dispatcher.register(store, (payload) => {
    const action = payload.action; // this is our action from handleViewAction
    switch (action.actionType) {
        case Actions.GET_CHANGE_REQUESTS:
            controller.getChangeRequests(action.environment, action.committed);
            break;
        case Actions.GET_CHANGE_REQUEST:
            controller.getChangeRequest(action.id);
            break;
        case Actions.UPDATE_CHANGE_REQUEST:
            controller.updateChangeRequest(action.changeRequest);
            break;
        case Actions.DELETE_CHANGE_REQUEST:
            controller.deleteChangeRequest(action.id, action.cb);
            break;
        case Actions.ACTION_CHANGE_REQUEST:
            controller.actionChangeRequest(action.id, action.action, action.cb);
            break;
    }
});
controller.store = store;
module.exports = controller.store;
