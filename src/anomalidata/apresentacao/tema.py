"""Paleta e estilos da interface desktop."""

from tkinter import font, ttk

FUNDO = "#edf3f3"
SUPERFICIE = "#ffffff"
TEXTO = "#142e31"
SECUNDARIO = "#4d6467"
BORDA = "#d7e3e2"
VERDE = "#087460"
VERDE_ESCURO = "#055846"
SIDEBAR = "#102e32"
SIDEBAR_ATIVA = "#234b4d"
MENTA = "#a9e4d3"
FONTE = "DejaVu Sans"
FUNDO_EVIDENCIA = "#edf6f3"


def configurar_tema(raiz) -> None:
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    raiz.configure(background=FUNDO)
    font.nametofont("TkDefaultFont", root=raiz).configure(family=FONTE, size=10)
    raiz.option_add("*TCombobox*Listbox.font", (FONTE, 10))
    estilo.configure(".", font=(FONTE, 10), foreground=TEXTO, background=FUNDO)
    estilo.configure("TFrame", background=FUNDO)
    estilo.configure("Superficie.TFrame", background=SUPERFICIE, relief="solid",
                     borderwidth=1, bordercolor=BORDA)
    estilo.configure("Interno.TFrame", background=SUPERFICIE)
    estilo.configure("Menu.TFrame", background=SIDEBAR)
    estilo.configure("Marca.TLabel", background=SIDEBAR, foreground=SUPERFICIE,
                     font=(FONTE, 15, "bold"))
    estilo.configure("MarcaIcone.TLabel", background=MENTA, foreground=SIDEBAR,
                     font=(FONTE, 10, "bold"), padding=(8, 6))
    estilo.configure("MenuNota.TLabel", background=SIDEBAR, foreground=MENTA,
                     font=(FONTE, 9))
    estilo.configure("Titulo.TLabel", font=(FONTE, 21, "bold"))
    estilo.configure("Subtitulo.TLabel", foreground=SECUNDARIO)
    estilo.configure("Secao.TLabel", background=SUPERFICIE, font=(FONTE, 12, "bold"))
    estilo.configure("Campo.TLabel", background=SUPERFICIE, font=(FONTE, 10, "bold"))
    estilo.configure("Dica.TLabel", background=SUPERFICIE, foreground=SECUNDARIO,
                     font=(FONTE, 9))
    estilo.configure("Evidencia.TFrame", background=FUNDO_EVIDENCIA)
    estilo.configure("EvidenciaRotulo.TLabel", background=FUNDO_EVIDENCIA,
                     foreground=SECUNDARIO, font=(FONTE, 9))
    estilo.configure("EvidenciaValor.TLabel", background=FUNDO_EVIDENCIA,
                     foreground=TEXTO, font=(FONTE, 10, "bold"))
    estilo.configure("EvidenciaDesvio.TLabel", background=FUNDO_EVIDENCIA,
                     foreground=VERDE_ESCURO, font=(FONTE, 12, "bold"))
    estilo.configure("Metrica.TLabel", background=SUPERFICIE, foreground=VERDE_ESCURO,
                     font=(FONTE, 20, "bold"))
    estilo.configure("Status.TLabel", foreground=SECUNDARIO, font=(FONTE, 9))
    estilo.configure("TButton", padding=(10, 7), background=SUPERFICIE,
                     bordercolor=BORDA, lightcolor=SUPERFICIE, darkcolor=SUPERFICIE)
    estilo.map("TButton", background=[("active", "#e4f1ee")],
               foreground=[("disabled", "#687c7d")])
    estilo.configure("Acao.TButton", background=VERDE, foreground=SUPERFICIE,
                     padding=(12, 8), font=(FONTE, 10, "bold"),
                     bordercolor=VERDE, lightcolor=VERDE, darkcolor=VERDE)
    estilo.map("Acao.TButton", background=[("disabled", "#d3e0de"), ("active", VERDE_ESCURO)],
               foreground=[("disabled", "#52696b"), ("!disabled", SUPERFICIE)])
    for nome, cor in (("MenuItem", SIDEBAR), ("MenuAtivo", SIDEBAR_ATIVA)):
        classe = f"{nome}.TButton"
        estilo.configure(classe, background=cor, foreground=SUPERFICIE, anchor="w",
                         padding=(11, 11), bordercolor=cor, lightcolor=cor, darkcolor=cor)
        estilo.map(classe, background=[("active", SIDEBAR_ATIVA)])
    estilo.configure("Workspace.TNotebook", background=FUNDO, borderwidth=0,
                     tabmargins=0, padding=0)
    estilo.layout("Workspace.TNotebook.Tab", [])
    for classe in ("TEntry", "TCombobox"):
        estilo.configure(classe, fieldbackground=SUPERFICIE, background=SUPERFICIE,
                         bordercolor=BORDA, padding=7, insertcolor=TEXTO)
        estilo.map(classe, fieldbackground=[("readonly", SUPERFICIE)],
                   bordercolor=[("focus", VERDE)])
    estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE,
                     rowheight=32, borderwidth=0, font=(FONTE, 10))
    estilo.configure("Treeview.Heading", background="#e9f2f0", foreground=TEXTO,
                     relief="flat", padding=(8, 7), font=(FONTE, 9, "bold"))
    estilo.map("Treeview", background=[("selected", "#c5ebdf")],
               foreground=[("selected", "#123a33")])
    estilo.configure("Horizontal.TProgressbar", background=VERDE, troughcolor="#e1ecea",
                     bordercolor=BORDA, lightcolor=VERDE, darkcolor=VERDE)
