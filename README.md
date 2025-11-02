# Trabalho Prático - Sistemas Operacionais: Gerenciamento de Memória

**Universidade Federal do Amazonas (UFAM) - ICET**  
**Curso de Sistemas de Informação**

## 📋 Visão Geral do Projeto

Este repositório é dedicado ao desenvolvimento do Trabalho Prático da disciplina de Sistemas Operacionais. O objetivo principal é consolidar o conhecimento adquirido, aprofundando a pesquisa no tema **Gerenciamento de Memória**, um dos tópicos centrais da disciplina.

O projeto envolve:
- Pesquisa teórica aprofundada
- Desenvolvimento de uma aplicação interativa para simular conceitos de gerenciamento de memória
- Criação de material para apresentação

## 👥 Grupo 4: Integrantes

- **Felipe Rangel**
- **Nadia Leão**
- **Oliviê Kalil**
- **Marcos Gabriel**

## 🖥️ Simulador de Gerenciamento de Memória

### 📸 Sobre o Simulador

Desenvolvemos um **simulador interativo em Python usando Tkinter** que demonstra visualmente os principais conceitos de gerenciamento de memória estudados na disciplina.

### ✨ Funcionalidades

#### 📄 **Aba Paginação**
- Simulação de algoritmos de substituição de páginas:
  - **FIFO** (First In First Out)
  - **LRU** (Least Recently Used)
  - **OPT** (Optimal)
- Ajuste dinâmico do número de frames (2-6)
- Adição de páginas aleatórias ou sequência padrão
- Execução passo a passo ou automática
- Estatísticas em tempo real:
  - Page Faults
  - Page Hits
  - Taxa de acerto
- Visualização colorida do estado da memória

#### 🔷 **Aba Segmentação**
- Criação de segmentos de tamanho variável (2-4 blocos)
- Algoritmo First Fit para alocação
- Alocação e liberação de segmentos na memória
- Visualização da fragmentação externa
- Estatísticas de ocupação da memória
- Cores distintas para cada segmento

#### 🔄 **Aba Swapping**
- Criação de processos com tamanhos variáveis
- Simulação de Swap In (disco/swap → RAM)
- Simulação de Swap Out (RAM → swap)
- Visualização dos processos em diferentes locais:
  - 🟢 RAM
  - 🔴 SWAP
  - ⚪ Disco
- Estatísticas de utilização de RAM e SWAP
- Demonstração da pressão de memória

### 🚀 Como Executar o Simulador

#### Requisitos
- Python 3.7 ou superior
- Tkinter (geralmente incluído na instalação padrão do Python)

#### Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/gerenciamento-memoria-ufam.git
cd gerenciamento-memoria-ufam
```

2. Execute o simulador:
```bash
python src/simulador_memoria/memory_simulator.py
```

ou no Windows:
```bash
python memory_simulator.py
```

### 🎯 Uso na Apresentação

O simulador foi desenvolvido especialmente para apresentações didáticas:

1. **Interface intuitiva** - Fácil de navegar durante a apresentação
2. **Visual atrativo** - Cores e animações chamam atenção
3. **Interativo** - Permite demonstrar conceitos em tempo real
4. **Completo** - Cobre os três principais conceitos do trabalho
5. **Didático** - Cada aba possui explicações dos conceitos

### 💡 Dicas para Apresentação

- **Paginação**: Compare os três algoritmos com a mesma sequência de páginas
- **Segmentação**: Demonstre o problema da fragmentação externa criando e removendo segmentos
- **Swapping**: Simule um cenário de pressão de memória enchendo a RAM

## 📁 Estrutura do Repositório

```
gerenciamento-memoria-ufam/
│
├── docs/
│   ├── TP1_SO.pdf                    # Trabalho escrito completo
│   ├── conclusoes_individuais/        # Conclusões de cada membro
│   ├── relatorios_reunioes.md        # Registro dos encontros
│   └── .gitkeep
│
├── src/
│   └── simulador_memoria/
│       └── memory_simulator.py        # Simulador interativo
│
├── presentation/
│   └── slides.pdf                     # Slides da apresentação
│
├── references/
│   └── artigos_e_materiais.md        # Materiais de pesquisa
│
├── LICENSE                            # Licença MIT
└── README.md                          # Este arquivo
```

## ✅ Checklist da Pesquisa: Tópicos Obrigatórios

### Conceitos Fundamentais
- [x] Alocação Contígua
- [x] Alocação Não Contígua
- [x] Hierarquia de Memória

### Técnicas de Gerenciamento
- [x] Paginação
- [x] Segmentação

### Memória Virtual
- [x] Conceito de Memória Virtual
- [x] Swapping
- [x] Algoritmos de Substituição de Páginas (FIFO, LRU, OPT)

### Análise de Implementações
- [x] Evolução histórica das técnicas (anos 1950 até presente)
- [x] Implementações em diferentes Sistemas Operacionais:
  - Linux (Kernel 6.x)
  - Windows (10/11 e Server)
  - macOS (Darwin/XNU)
  - FreeBSD
  - Android

## 📦 Checklist dos Entregáveis

### Pesquisa e Documentação
- [x] Discussão crítica em grupo sobre o tema
- [x] Trabalho escrito completo (30 páginas)
- [x] Relatório dos encontros da equipe
- [ ] Conclusão individual de cada aluno

### Desenvolvimento
- [x] Aplicação de Simulação Interativa
  - [x] Simulador de Paginação
  - [x] Simulador de Segmentação
  - [x] Simulador de Swapping

### Apresentação
- [ ] Slides para o seminário
- [x] Material visual (simulador) para demonstração

## 📚 Principais Conceitos Abordados

### Paginação
- Divisão da memória em blocos de tamanho fixo
- Tabela de páginas para mapeamento
- Algoritmos de substituição (FIFO, LRU, OPT)
- Page faults e page hits
- TLB (Translation Lookaside Buffer)

### Segmentação
- Divisão lógica da memória
- Segmentos de tamanho variável
- Tabela de segmentos (base e limite)
- Fragmentação externa
- Proteção e compartilhamento

### Swapping
- Movimentação de processos entre RAM e disco
- Swap In e Swap Out
- Espaço de swap
- Impacto no desempenho
- Gerenciamento de memória sob pressão

## 🔧 Tecnologias Utilizadas

- **Python 3.12** - Linguagem de programação
- **Tkinter** - Interface gráfica
- **LaTeX** - Formatação do trabalho escrito
- **Git/GitHub** - Controle de versão

## 📅 Cronograma

| Data | Atividade | Status |
|------|-----------|--------|
| Outubro 2024 | Pesquisa e estudo dos conceitos | ✅ Concluído |
| Outubro 2025 | Desenvolvimento do simulador | ✅ Concluído |
| Outubro 2025 | Redação do trabalho escrito | ✅ Concluído |
| Novembro 2025 | Preparação da apresentação | 🔄 Em andamento |
| 10/11/2025 | **Apresentação e Entrega Final** | ⏳ Pendente |

## 📖 Referências Principais

1. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts* (10th ed.). Wiley.
2. Tanenbaum, A. S., & Bos, H. (2014). *Modern Operating Systems* (4th ed.). Pearson.
3. Love, R. (2010). *Linux Kernel Development* (3rd ed.). Addison-Wesley.
4. Russinovich, M. E., Solomon, D. A., & Ionescu, A. (2017). *Windows Internals* (7th ed.). Microsoft Press.

## 👨‍🏫 Informações da Disciplina

- **Disciplina:** Sistemas Operacionais
- **Professor:** Dr. Rallyson dos Santos Ferreira
- **E-mail para entrega:** `rallysonferreira@gmail.com`
- **Instituição:** UFAM - Instituto de Ciências Exatas e Tecnologia (ICET)
- **Curso:** Sistemas de Informação
- **Ano:** 2025

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuições

Este é um projeto acadêmico desenvolvido pelo Grupo 4. Contribuições e sugestões são bem-vindas através de issues e pull requests.

## 📞 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato com qualquer membro do grupo através do GitHub.

---

**Desenvolvido com 💙 pelo Grupo 4 - UFAM/ICET 2025**

*"A educação é a arma mais poderosa que você pode usar para mudar o mundo." - Nelson Mandela*
