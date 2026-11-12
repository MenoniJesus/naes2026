from django import forms

from .models import ConfiguracaoIA, CotaUsuarioIA


class ConfiguracaoIAForm(forms.ModelForm):
    """A chave nunca é exibida de volta: em branco mantém a atual."""

    remover_chave = forms.BooleanField(
        required=False,
        label="Remover a chave salva (passar a usar ANTHROPIC_API_KEY do ambiente)",
    )

    class Meta:
        model = ConfiguracaoIA
        fields = [
            "ativo", "modelo", "api_key", "max_tokens", "esforco",
            "usar_fallback", "timeout_segundos", "cota_mensal_padrao",
        ]
        widgets = {
            "api_key": forms.PasswordInput(render_value=False, attrs={"autocomplete": "off"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chave_atual = self.instance.api_key
        if self._chave_atual:
            self.fields["api_key"].help_text = (
                f"Há uma chave salva (termina em …{self._chave_atual[-4:]}). "
                "Deixe em branco para mantê-la."
            )
        else:
            self.fields.pop("remover_chave")

    def clean_modelo(self):
        modelo = self.cleaned_data["modelo"].strip()
        if not modelo.startswith("claude-"):
            raise forms.ValidationError("Informe um ID de modelo Claude, ex.: claude-opus-5-5.")
        return modelo

    def clean_api_key(self):
        chave = self.cleaned_data["api_key"].strip()
        return chave or self._chave_atual

    def clean_max_tokens(self):
        max_tokens = self.cleaned_data["max_tokens"]
        if not 256 <= max_tokens <= 64000:
            raise forms.ValidationError("Use um valor entre 256 e 64.000.")
        return max_tokens

    def clean(self):
        dados = super().clean()
        # remover_chave é validado depois de api_key, por isso a regra fica aqui.
        if dados.get("remover_chave"):
            dados["api_key"] = ""
        return dados


class CotaUsuarioIAForm(forms.ModelForm):
    class Meta:
        model = CotaUsuarioIA
        fields = ["habilitado", "cota_mensal", "observacao"]
