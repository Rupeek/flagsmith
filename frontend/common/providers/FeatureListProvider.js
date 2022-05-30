import React, { Component } from 'react';
import FeatureListStore from '../stores/feature-list-store';

const FeatureListProvider = class extends Component {
    static displayName = 'FeatureListProvider'

    constructor(props, context) {
        super(props, context);
        this.state = {
            isSaving: FeatureListStore.isSaving,
            isLoading: FeatureListStore.isLoading,
            environmentFlags: FeatureListStore.getEnvironmentFlags(),
            projectFlags: FeatureListStore.getProjectFlags(),
            lastSaved: FeatureListStore.getLastSaved(),
            influxData: FeatureListStore.getFlagInfluxData(),
        };
        ES6Component(this);
        this.listenTo(FeatureListStore, 'change', () => {
            this.setState({
                isSaving: FeatureListStore.isSaving,
                isLoading: FeatureListStore.isLoading,
                environmentFlags: FeatureListStore.getEnvironmentFlags(),
                lastSaved: FeatureListStore.getLastSaved(),
                projectFlags: FeatureListStore.getProjectFlags(),
                influxData: FeatureListStore.getFlagInfluxData(),
            });
        });

        this.listenTo(FeatureListStore, 'saved', () => {
            this.props.onSave && this.props.onSave();
        });

        this.listenTo(FeatureListStore, 'problem', () => {
            this.setState({
                isSaving: FeatureListStore.isSaving,
                isLoading: FeatureListStore.isLoading,
                error: FeatureListStore.error,
                lastSaved: FeatureListStore.getLastSaved(),
                influxData: FeatureListStore.getFlagInfluxData(),
            });
            this.props.onError && this.props.onError(FeatureListStore.error);
        });
    }

    toggleFlag = (i, environments, comment, environmentFlags) => {
        AppActions.toggleFlag(i, environments, comment, environmentFlags);
    };

    setFlag = (i, flag, environments) => {
        AppActions.setFlag(i, flag, environments);
    };

    createFlag = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides) => {
        AppActions.createFlag(projectId, environmentId, flag, segmentOverrides);
    };

    editFlag = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides) => {
        AppActions.editFlag(projectId, Object.assign({}, projectFlag, flag, {
            multivariate_options: flag.multivariate_options && flag.multivariate_options.map((v) => {
                const matchingProjectVariate = (projectFlag.multivariate_options && projectFlag.multivariate_options.find(p => p.id === v.id)) || v;
                return {
                    ...v,
                    default_percentage_allocation: matchingProjectVariate.default_percentage_allocation,
                };
            }),
        }), (newProjectFlag) => {
            AppActions.editEnvironmentFlag(projectId, environmentId, flag, newProjectFlag, {
                ...environmentFlag,
                multivariate_feature_state_values: flag.multivariate_options,
            }, segmentOverrides);
        });
    };

    editFlagValue = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides) => {
        AppActions.editFlag(projectId, Object.assign({}, projectFlag, {
            multivariate_options: flag.multivariate_options && flag.multivariate_options.map((v) => {
                const matchingProjectVariate = (projectFlag.multivariate_options && projectFlag.multivariate_options.find(p => p.id === v.id)) || v;
                return {
                    ...v,
                    default_percentage_allocation: matchingProjectVariate.default_percentage_allocation,
                };
            }),
        }), (newProjectFlag) => {
            AppActions.editEnvironmentFlag(projectId, environmentId, flag, newProjectFlag, {
                ...environmentFlag,
                multivariate_feature_state_values: flag.multivariate_options,
            }, null, "VALUE");
        });
    };

    editFlagSegments = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides) => {
        AppActions.editFlag(projectId, Object.assign({}, projectFlag, {
            multivariate_options: flag.multivariate_options && flag.multivariate_options.map((v) => {
                const matchingProjectVariate = (projectFlag.multivariate_options && projectFlag.multivariate_options.find(p => p.id === v.id)) || v;
                return {
                    ...v,
                    default_percentage_allocation: matchingProjectVariate.default_percentage_allocation,
                };
            }),
        }), (newProjectFlag) => {
            AppActions.editEnvironmentFlag(projectId, environmentId, flag, newProjectFlag, {
                ...environmentFlag,
                multivariate_feature_state_values: flag.multivariate_options,
            }, segmentOverrides, "SEGMENT");
        });
    };

    editFlagSettings = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides) => {
        AppActions.editFlag(projectId, Object.assign({}, projectFlag, flag, {
            multivariate_options: flag.multivariate_options && flag.multivariate_options.map((v) => {
                const matchingProjectVariate = (projectFlag.multivariate_options && projectFlag.multivariate_options.find(p => p.id === v.id)) || v;
                return {
                    ...v,
                    default_percentage_allocation: matchingProjectVariate.default_percentage_allocation,
                };
            }),
        }), ()=>{
            FeatureListStore.isSaving = false;
            FeatureListStore.trigger("saved")
            FeatureListStore.trigger("change")
        });
    };

    createChangeRequest = (projectId, environmentId, flag, projectFlag, environmentFlag, segmentOverrides, changeRequest, commit) => {
        AppActions.editFlag(projectId, Object.assign({}, projectFlag, flag, {
            multivariate_options: flag.multivariate_options && flag.multivariate_options.map((v) => {
                const matchingProjectVariate = (projectFlag.multivariate_options && projectFlag.multivariate_options.find(p => p.id === v.id)) || v;
                return {
                    ...v,
                    default_percentage_allocation: matchingProjectVariate.default_percentage_allocation,
                };
            }),
        }), (newProjectFlag) => {
            AppActions.editEnvironmentFlagChangeRequest(projectId, environmentId, flag, newProjectFlag, {
                ...environmentFlag,
                multivariate_feature_state_values: flag.multivariate_options,
            }, segmentOverrides, changeRequest, commit);
        });
    };

    removeFlag = (projectId, flag) => {
        AppActions.removeFlag(projectId, flag);
    };

    render() {
        return (
            this.props.children(
                {
                    ...this.state,
                },
                {
                    environmentHasFlag: FeatureListStore.hasFlagInEnvironment,
                    toggleFlag: this.toggleFlag,
                    setFlag: this.setFlag,
                    createFlag: this.createFlag,
                    createChangeRequest: this.createChangeRequest,
                    editFlag: this.editFlag,
                    editFlagValue: this.editFlagValue,
                    editFlagSettings: this.editFlagSettings,
                    editFlagSegments: this.editFlagSegments,
                    removeFlag: this.removeFlag,
                },
            )
        );
    }
};

FeatureListProvider.propTypes = {};

module.exports = FeatureListProvider;
