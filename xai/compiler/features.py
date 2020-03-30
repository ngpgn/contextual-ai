#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2019 SAP SE or an SAP affiliate company. All rights reserved
# ============================================================================
""" Compiler - Features """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from xai.compiler.base import Dict2Obj
from xai.formatter import Report
from xai.model.interpreter import FeatureInterpreter


################################################################################
### Feature Importance Ranking
################################################################################
class FeatureImportanceRanking(Dict2Obj):
    """
    Compiler for Feature Importance Ranking

    Param:
        package (str, Optional): component package name
        module (str, Optional): component module name
        class (str): component class name

    Attr:
        trained_model (str): path to trained model pickle
        train_data (str): path to training sample data
        feature_names (str, Optional): array-list of feature names
        method: (str, Optional) interpreter method, default = 'default'
        threshold (number, Optional): importance threshold, default 0.005

    Example:
        "component": {
            "package": "xai",
            "module": "compiler",
            "class": "FeatureImportanceRanking",
            "attr": {
                "trained_model": "./sample_input/model.pkl",
                "train_data": "./sample_input/train.csv",
                "feature_names": "./sample_input/feature_name.csv",
                "method": "default"
                "threshold": 0.005
            }
        }
    """
    schema = {
        "type": "object",
        "properties": {
            "trained_model": {"type": ["string", "object"]},
            "train_data": {" type": ["string", "object"]},
            "feature_names": {"type": ["string", "object"]},
            "method": {
                "enum": ["default", "shap"],
                "default": "default"
            },
            "threshold": {
                "type": "number",
                "default": 0.005
            }
        },
        "required": ["trained_model", "train_data"]
    }

    def __init__(self, dictionary):
        """
        Init

        Args:
            dictionary (dict): attribute to set
        """
        super(FeatureImportanceRanking, self).__init__(dictionary,
                                                       schema=self.schema)

    def __call__(self, report: Report, level: int):
        """
        Execution

        Args:
            report (Report): report object
            level (int): content level
        """
        super(FeatureImportanceRanking, self).__call__(report=report,
                                                       level=level)
        threshold = self.assert_attr(key='threshold', default=0.005)
        method = self.assert_attr(key='method', default='default')
        # -- Load Model --
        model_var = self.assert_attr(key='trained_model')
        model = self.load_data(model_var)
        # -- Check if feature names is set --
        header = True
        fn_var = self.assert_attr(key='feature_names', optional=True)
        feature_names = None
        if fn_var is not None:
            feature_names = self.load_data(fn_var)
            header = False
        # -- Load Training Data for default method --
        data_var = self.assert_attr(key='train_data',
                                    optional=(method=='default'))
        train_data = None
        if data_var is not None:
            train_data = self.load_data(data_var, header=header)
            if  header:
                feature_names = train_data.columns

        # -- Get Feature Importance --
        fi = FeatureInterpreter(feature_names=feature_names)
        rank = fi.get_feature_importance_ranking(trained_model=model,
                                                 train_x=train_data,
                                                 method=method)
        # -- Add Feature Importance --
        report.detail.add_feature_importance(
            importance_ranking=rank, importance_threshold=threshold)
