#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy
import re

from functools import partial
from django.contrib import admin
from django.forms.models import modelformset_factory
from django.contrib.admin.utils import flatten_fieldsets

class FieldLevelAdmin(admin.ModelAdmin):
    """
    A subclass of ModelAdmin that provides hooks for setting field-level 
    permissions based on object or request properties. Intended to be used as an 
    abstract base class replacement for ModelAdmin, with can_change_inline() and 
    can_change_field() customized to each use.
    """
    def get_all_viewperms(self, request):
        """
        获取所有的view权限
        """
        viewperms = tuple()
        for perm in request.user.get_all_permissions():
            if self.opts.app_label in perm and 'view' in perm:
                short_cut = "_".join(".".join(perm.split('.')[1:]).split('_')[1:])
                # 如果拥有查看全部的
                if short_cut == "all":
                    fields = self.model._meta.get_all_field_names()
                    return tuple(fields)
                else:
                    viewperms += (short_cut,)
        return viewperms

    def get_readonly_fields(self,request, obj=None, origin=True):
        all_view_permissions = self.get_all_viewperms(request) if not request.user.is_superuser else ()
        return tuple(set(self.readonly_fields)|set(all_view_permissions))


    def get_changelist_formset(self, request, **kwargs):
        """
        Returns a FormSet class for use on the changelist page if list_editable
        is used.
        """
        defaults = {
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        if 'fields' in defaults:
            fields=defaults['fields']
            del defaults['fields']
        else:
            fields=self.list_editable,
        return modelformset_factory(self.model,
            self.get_changelist_form(request), fields=fields, extra=0, **defaults)