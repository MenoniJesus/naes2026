---
name: novo-crud
description: Cria um model novo com CRUD completo seguindo os padrões do SobraNada (CBVs com mixins de dono e mensagens, template genérico de formulário, listagem com DataTables, filtro e paginação, rotas e testes). Use ao adicionar uma entidade nova ou telas de cadastro.
---

# Novo CRUD no SobraNada

Siga a ordem abaixo. Use um model existente como referência (`Notificacao` é o mais simples com
dono; `Produto` mostra dono via relação).

## 1. Model (`sobraNada/models.py`)

- Nomes em português; `verbose_name` em todo campo e no `Meta` (`verbose_name`, `verbose_name_plural`).
  As mensagens do `MensagemMixin` usam o `verbose_name` do model.
- `ordering` no `Meta` e um `__str__` legível.
- Se o registro pertence a um usuário: `user = models.ForeignKey(User, on_delete=models.PROTECT)`.
- Se o `__str__` acessa uma relação, anote para lembrar do `select_related` nas telas.
- Rode `makemigrations` e confira a migração gerada.

## 2. Form (`sobraNada/forms.py`)

- `ModelForm` **sem** o campo `user` (ele é preenchido na view).
- Campos de data/hora com `WIDGET_DATA` / `WIDGET_HORA`.
- Se um `<select>` mostra objetos cujo `__str__` acessa relação, ajuste o `queryset` no `__init__`
  com `select_related` (ex.: `EnderecoForm`).

## 3. Views (`sobraNada/views.py`)

```python
class XCreate(MensagemMixin, BaseLoginMixin, CreateView):
    model = X
    form_class = XForm
    template_name = 'sobraNada/form.html'
    success_url = reverse_lazy('x-list')
    extra_context = {'titulo': 'Cadastro de X', 'botao': 'Criar X'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class XUpdate(MensagemMixin, BaseLoginMixin, DonoMixin, UpdateView): ...
class XDelete(MensagemMixin, BaseLoginMixin, DonoMixin, DeleteView):
    extra_context = {'titulo': 'Excluir X', 'botao': 'Sim, excluir!'}  # ativa o Bootbox
class XList(BaseLoginMixin, DonoMixin, ListView):
    paginate_by = 30
    def get_queryset(self):
        qs = super().get_queryset().select_related(...)
        self.filterset = XFilter(self.request.GET, queryset=qs)
        return self.filterset.qs
class XDetail(BaseLoginMixin, DonoMixin, DetailView): ...
```

- `MensagemMixin` vem **primeiro**; `DonoMixin` usa `campo_dono` (padrão `'user'`; via relação,
  ex.: `'estabelecimento__user'`).
- Telas só de admin: `GroupRequiredMixin` com `group_required = ['admin']`.

## 4. Filtro (`sobraNada/filters.py`)

`django_filters.FilterSet` com `CharFilter(lookup_expr='icontains')` para texto. Se houver
`ModelChoiceFilter` de um model com `__str__` relacional, passe um `queryset` com prefetch.

## 5. Templates

- Formulário: reutilize `sobraNada/form.html` (não crie um novo).
- `sobraNada/templates/sobraNada/list/x.html` e `detail/x.html` copiando um existente:
  tabela com `class="table table-datatable"`, form do filtro com `{{ filter.form|crispy }}`,
  `{% include "sobraNada/includes/pagination.html" %}` no fim.
- Mostre editar/excluir só para o dono: `{% if obj.user_id == user.id %}`.

## 6. Rotas, menu e painel

- `sobraNada/urls.py`: `cadastrar/x/`, `atualizar/x/<int:pk>/`, `excluir/x/<int:pk>/`,
  `listar/x/`, `detalhar/x/<int:pk>/`, nomes `x-create`, `x-update`, `x-delete`, `x-list`, `x-detail`.
- Adicione nos dropdowns "Cadastrar" e "Listar" de `website/templates/website/modelo2.html` e um
  card em `website/templates/website/hub.html`.
- Registre no `sobraNada/admin.py`.

## 7. Testes (`sobraNada/tests/test_views.py`)

Cubra pelo menos: mensagem de sucesso no cadastro, outro usuário recebe 404 em update/delete, e
adicione a rota da listagem em `QueriesTests` para garantir que não há N+1.

```bash
DATABASE_URL=sqlite:///test_local.sqlite3 .venv/bin/pytest -q
```
