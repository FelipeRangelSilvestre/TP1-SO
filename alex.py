#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Trânsito Inteligente - VERSÃO PROFISSIONAL
Malha 10x10 com 100+ interseções, vias de mão única, becos e visual Google Maps
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
from datetime import datetime
import time
import random

# =========================================================================
# ESTRUTURAS DE DADOS
# =========================================================================

class NoAVL:
    def __init__(self, id_evento, timestamp, tipo, localizacao, aumento_tempo):
        self.id = id_evento
        self.timestamp = timestamp
        self.tipo = tipo
        self.localizacao = localizacao
        self.aumento_tempo = aumento_tempo
        self.esquerda = None
        self.direita = None
        self.altura = 1

class ArvoreAVL:
    def __init__(self):
        self.root = None
        self.total_eventos = 0
        self.eventos = {}
    
    def inserir(self, id_evento, timestamp, tipo, localizacao, aumento_tempo):
        self.total_eventos += 1
        self.eventos[id_evento] = NoAVL(id_evento, timestamp, tipo, localizacao, aumento_tempo)
    
    def remover(self, id_evento):
        if id_evento in self.eventos:
            del self.eventos[id_evento]
            self.total_eventos -= 1
    
    def buscar(self, id_evento):
        return self.eventos.get(id_evento)
    
    def listar_todos(self):
        return list(self.eventos.values())

class GrafoPonderado:
    def __init__(self):
        self.vertices = set()
        self.arestas = {}
    
    def adicionar_vertice(self, vertice):
        self.vertices.add(vertice)
        if vertice not in self.arestas:
            self.arestas[vertice] = {}
    
    def adicionar_aresta(self, origem, destino, peso):
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self.arestas[origem][destino] = peso
        self.arestas[destino][origem] = peso
    
    def adicionar_aresta_direcionada(self, origem, destino, peso):
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        if origem not in self.arestas:
            self.arestas[origem] = {}
        self.arestas[origem][destino] = peso
    
    def obter_peso(self, origem, destino):
        return self.arestas.get(origem, {}).get(destino)
    
    def total_vertices(self):
        return len(self.vertices)
    
    def total_arestas(self):
        count = 0
        for d in self.arestas.values():
            count += len(d)
        return count
    
    def obter_todas_arestas(self):
        lista = []
        for o, destinos in self.arestas.items():
            for d, peso in destinos.items():
                lista.append((o, d, peso))
        return lista
    
    def atualizar_peso(self, origem, destino, novo_peso):
        if origem in self.arestas and destino in self.arestas[origem]:
            self.arestas[origem][destino] = novo_peso
    
    def dijkstra(self, origem, destino):
        import heapq
        
        if origem not in self.vertices or destino not in self.vertices:
            return None, None
        
        distancias = {v: float('inf') for v in self.vertices}
        distancias[origem] = 0
        predecessores = {v: None for v in self.vertices}
        heap = [(0, origem)]
        visitados = set()
        
        while heap:
            dist_atual, vertice_atual = heapq.heappop(heap)
            
            if vertice_atual in visitados:
                continue
            
            visitados.add(vertice_atual)
            
            if vertice_atual == destino:
                break
            
            if vertice_atual in self.arestas:
                for vizinho, peso in self.arestas[vertice_atual].items():
                    if vizinho not in visitados:
                        nova_dist = dist_atual + peso
                        if nova_dist < distancias[vizinho]:
                            distancias[vizinho] = nova_dist
                            predecessores[vizinho] = vertice_atual
                            heapq.heappush(heap, (nova_dist, vizinho))
        
        if distancias[destino] == float('inf'):
            return None, None
        
        caminho = []
        atual = destino
        while atual is not None:
            caminho.insert(0, atual)
            atual = predecessores[atual]
        
        return caminho, distancias[destino]

# =========================================================================
# SISTEMA DE TRÂNSITO
# =========================================================================

class SistemaTransitoMelhorado:
    VELOCIDADE_PADRAO = 60.0
    VELOCIDADES_EVENTO = {'acidente': 10.0, 'obra': 20.0, 'engarrafamento': 30.0}
    
    def __init__(self, grafo, avl):
        self.grafo = grafo
        self.avl = avl
        self.proximo_id_evento = 1
        self.velocidades = {}
        self.distancias = {}
    
    def _calcular_tempo(self, distancia_km, velocidade_kmh):
        if velocidade_kmh <= 0:
            return float('inf')
        return (distancia_km / velocidade_kmh) * 60
    
    def adicionar_via(self, origem, destino, distancia_km, velocidade_kmh=None):
        if velocidade_kmh is None:
            velocidade_kmh = self.VELOCIDADE_PADRAO
        tempo_minutos = self._calcular_tempo(distancia_km, velocidade_kmh)
        self.grafo.adicionar_aresta(origem, destino, tempo_minutos)
        self.velocidades[f"{origem}-{destino}"] = velocidade_kmh
        self.velocidades[f"{destino}-{origem}"] = velocidade_kmh
        self.distancias[f"{origem}-{destino}"] = distancia_km
        self.distancias[f"{destino}-{origem}"] = distancia_km
        return True

    def obter_info_via(self, origem, destino):
        tempo = self.grafo.obter_peso(origem, destino)
        velocidade = self.velocidades.get(f"{origem}-{destino}", self.VELOCIDADE_PADRAO)
        distancia = self.distancias.get(f"{origem}-{destino}")
        
        if tempo is None:
            return None
        
        if distancia is None:
            distancia = (tempo / 60) * velocidade
        
        return {'distancia_km': distancia, 'velocidade_kmh': velocidade, 'tempo_min': tempo}
    
    def registrar_evento(self, tipo, origem, destino):
        if self.grafo.obter_peso(origem, destino) is None and self.grafo.obter_peso(destino, origem) is not None:
            origem, destino = destino, origem
        
        info_antes = self.obter_info_via(origem, destino)
        if info_antes is None: 
            return False, "Via não encontrada"
        
        eventos_ativos = self.avl.listar_todos()
        evento_existente = next((ev for ev in eventos_ativos 
                                if ev.localizacao == f"{origem}-{destino}" 
                                or ev.localizacao == f"{destino}-{origem}"), None)

        if evento_existente:
            self.remover_evento(evento_existente.id)
        
        nova_velocidade = self.VELOCIDADES_EVENTO[tipo]
        distancia = info_antes['distancia_km']
        novo_tempo = self._calcular_tempo(distancia, nova_velocidade)
        
        self.grafo.atualizar_peso(origem, destino, novo_tempo)
        self.velocidades[f"{origem}-{destino}"] = nova_velocidade
        
        if self.grafo.obter_peso(destino, origem) is not None:
            self.grafo.atualizar_peso(destino, origem, novo_tempo)
            self.velocidades[f"{destino}-{origem}"] = nova_velocidade
        
        self.avl.inserir(self.proximo_id_evento, int(time.time()), tipo, f"{origem}-{destino}", 0)
        self.proximo_id_evento += 1
        return True, "Evento registrado"

    def remover_evento(self, id_evento):
        evento = self.avl.buscar(id_evento)
        if not evento: 
            return False, "Evento não encontrado"
        
        origem, destino = evento.localizacao.split('-')
        
        info = self.obter_info_via(origem, destino)
        if not info: 
            info = self.obter_info_via(destino, origem)
            if not info:
                return False, "Via não encontrada"

        distancia = info['distancia_km']
        tempo_normal = self._calcular_tempo(distancia, self.VELOCIDADE_PADRAO)
        
        self.grafo.atualizar_peso(origem, destino, tempo_normal)
        self.velocidades[f"{origem}-{destino}"] = self.VELOCIDADE_PADRAO
        
        if self.grafo.obter_peso(destino, origem) is not None:
            self.grafo.atualizar_peso(destino, origem, tempo_normal)
            self.velocidades[f"{destino}-{origem}"] = self.VELOCIDADE_PADRAO
             
        self.avl.remover(id_evento)
        return True, "Evento removido"

    def calcular_rota_rapida(self, origem, destino):
        caminho, tempo_total = self.grafo.dijkstra(origem, destino)
        
        if caminho is None: 
            return None, None, "Sem rota disponível"
        
        distancia_total = 0.0
        for i in range(len(caminho) - 1):
            o, d = caminho[i], caminho[i + 1]
            info = self.obter_info_via(o, d) 
            if info is None: 
                info = self.obter_info_via(d, o)
            
            if info: 
                distancia_total += info['distancia_km']
        
        velocidade_media = (distancia_total / (tempo_total / 60)) if tempo_total and tempo_total > 0 else 0
        
        return caminho, {
            'tempo_total_min': tempo_total, 
            'distancia_total_km': distancia_total, 
            'velocidade_media_kmh': velocidade_media
        }, "OK"

    def calcular_k_melhores_rotas(self, origem, destino, k=3):
        """Calcula K melhores rotas alternativas"""
        rotas = []
        
        # Primeira rota
        caminho, info, status = self.calcular_rota_rapida(origem, destino)
        if not caminho:
            return []
        
        rotas.append({'caminho': caminho, 'info': info, 'numero': 1})
        
        # Salva pesos originais
        pesos_originais = {}
        for o, d, peso in self.grafo.obter_todas_arestas():
            pesos_originais[(o, d)] = peso
        
        # Tenta encontrar rotas alternativas
        for tentativa in range(1, k):
            # Penaliza as arestas das rotas já encontradas
            for rota_existente in rotas:
                caminho_existente = rota_existente['caminho']
                for i in range(len(caminho_existente) - 1):
                    o, d = caminho_existente[i], caminho_existente[i + 1]
                    peso_atual = self.grafo.obter_peso(o, d)
                    if peso_atual:
                        self.grafo.atualizar_peso(o, d, peso_atual * 1.5)
            
            # Calcula nova rota
            caminho_alt, info_alt, _ = self.calcular_rota_rapida(origem, destino)
            
            # Restaura pesos
            for (o, d), peso in pesos_originais.items():
                self.grafo.atualizar_peso(o, d, peso)
            
            if caminho_alt and caminho_alt not in [r['caminho'] for r in rotas]:
                rotas.append({'caminho': caminho_alt, 'info': info_alt, 'numero': tentativa + 1})
        
        # Ordena por tempo
        rotas.sort(key=lambda r: r['info']['tempo_total_min'])
        for i, rota in enumerate(rotas):
            rota['numero'] = i + 1
        
        return rotas
        
    def estatisticas(self):
        num_vertices = len(self.grafo.vertices)
        total_distancia = 0.0
        
        arestas_contadas = set()
        for o, d, _ in self.grafo.obter_todas_arestas():
            par = tuple(sorted([o, d]))
            if par not in arestas_contadas:
                info = self.obter_info_via(o, d)
                if info:
                    total_distancia += info['distancia_km']
                arestas_contadas.add(par)
        
        total_vias_direcionais = self.grafo.total_arestas()

        stats = {
            'total_intersecoes': num_vertices, 
            'total_vias': total_vias_direcionais, 
            'vias_bidirecionais': len(arestas_contadas), 
            'vias_unidirecionais': total_vias_direcionais - 2 * len(arestas_contadas), 
            'becos_sem_saida': len([v for v in self.grafo.vertices if v.startswith('BECO')]), 
            'intersecoes_isoladas': len([v for v in self.grafo.vertices if v.startswith('ISOLADA')]), 
            'distancia_total_km': total_distancia, 
            'eventos_ativos': self.avl.total_eventos, 
            'eventos_por_tipo': {'acidente': 0, 'obra': 0, 'engarrafamento': 0}
        }
        
        for evento in self.avl.listar_todos():
            stats['eventos_por_tipo'][evento.tipo] += 1
        
        return stats

# =========================================================================
# INTERFACE GRÁFICA
# =========================================================================

class InterfaceTransitoMelhorada:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Trânsito Inteligente PRO 🗺️")
        
        self.root.geometry("1500x850")
        self.root.configure(bg="#1a1a2e")
        
        self.grafo = GrafoPonderado()
        self.avl = ArvoreAVL()
        self.sistema = SistemaTransitoMelhorado(self.grafo, self.avl)
        
        self.vertices_pos = {}
        self.caminho_atual = []
        self.caminhos_alternativos = []
        
        self.criar_menu()
        self.criar_interface()
        self.criar_dados_exemplo()
        
        self.root.update_idletasks() 
        self.calcular_layout_grid()
        
        self.root.after(100, self.desenhar_grafo)
        self.root.after(2000, self.simular_eventos_aleatorios)
    
    def _is_segment_on_path(self, origem, destino, path):
        if not path:
            return False
        for i in range(len(path) - 1):
            o, d = path[i], path[i + 1]
            if (o == origem and d == destino) or (o == destino and d == origem):
                return True
        return False

    def simular_eventos_aleatorios(self):
        tipos_evento = list(self.sistema.VELOCIDADES_EVENTO.keys())
        
        vias_candidatas = []
        processadas = set()
        for origem, destino, _ in self.grafo.obter_todas_arestas():
            par = tuple(sorted([origem, destino]))
            if par not in processadas and self.sistema.obter_info_via(origem, destino):
                vias_candidatas.append((origem, destino))
                processadas.add(par)
        
        if vias_candidatas:
            origem, destino = random.choice(vias_candidatas)
            
            eventos_ativos = self.sistema.avl.listar_todos()
            evento_na_via = next((ev for ev in eventos_ativos 
                                 if ev.localizacao == f"{origem}-{destino}" 
                                 or ev.localizacao == f"{destino}-{origem}"), None)
            
            chance = random.random()
            
            if evento_na_via:
                if chance < 0.3:
                    self.sistema.remover_evento(evento_na_via.id)
            else:
                if chance > 0.8:
                    tipo = random.choice(tipos_evento)
                    self.sistema.registrar_evento(tipo, origem, destino)
            
            self.atualizar_interface()
        
        self.root.after(5000, self.simular_eventos_aleatorios)

    def criar_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Sair", command=self.root.quit)

        menu_eventos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Eventos", menu=menu_eventos)
        menu_eventos.add_command(label="💥 Registrar Acidente", 
                                command=lambda: self.registrar_evento_dialog('acidente'))
        menu_eventos.add_command(label="🚧 Registrar Obra", 
                                command=lambda: self.registrar_evento_dialog('obra'))
        menu_eventos.add_command(label="🚦 Registrar Engarrafamento", 
                                command=lambda: self.registrar_evento_dialog('engarrafamento'))
        menu_eventos.add_separator()
        menu_eventos.add_command(label="Remover Evento", command=self.remover_evento_dialog)

        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Como Funciona", command=self.mostrar_como_funciona)
    
    def criar_interface(self):
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # PAINEL ESQUERDO - MAPA
        left_frame = tk.Frame(main_frame, bg="#FFFFFF", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        titulo_canvas = tk.Label(left_frame, text="🗺️ MALHA VIÁRIA - 100+ INTERSEÇÕES", 
                                bg="#FFFFFF", fg="#1a1a2e", 
                                font=("Arial", 16, "bold"))
        titulo_canvas.pack(pady=10)
        
        canvas_frame = tk.Frame(left_frame, bg="#FFFFFF")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#F4F2F1", highlightthickness=0) 
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        legenda_frame = tk.Frame(left_frame, bg="#FFFFFF")
        legenda_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(legenda_frame, 
                 text="🔵 Rota Principal | 🟢🟠🟣 Alternativas | 🔴 Evento/Lento | ⚪ Normal", 
                 bg="#FFFFFF", fg="black", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Label(legenda_frame, 
                 text="➡️ Via de Mão Única | 🚫 Beco Sem Saída | ⚠️ Área Isolada", 
                 bg="#FFFFFF", fg="#666", font=("Arial", 8)).pack(anchor="w", pady=(3,0))
        
        # PAINEL DIREITO - CONTROLES
        right_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.config(width=400)
        
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background="#16213e", borderwidth=0)
        style.configure('TNotebook.Tab', background="#0f3460", foreground="white", 
                       padding=[15, 8], font=("Arial", 10, "bold"))
        style.map('TNotebook.Tab', background=[('selected', '#00d4ff')],
                 foreground=[('selected', 'black')])
        
        self.criar_aba_rotas(notebook)
        self.criar_aba_eventos(notebook)
        self.criar_aba_estatisticas(notebook)

    def criar_aba_rotas(self, notebook):
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="🗺️ Rotas")
        
        titulo = tk.Label(frame, text="Cálculo de Rotas Inteligente", bg="#16213e", 
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        tk.Label(frame, text="📍 Origem:", bg="#16213e", fg="white", 
                font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_origem = ttk.Combobox(frame, state="readonly", font=("Arial", 11))
        self.combo_origem.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame, text="📍 Destino:", bg="#16213e", fg="white", 
                font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_destino = ttk.Combobox(frame, state="readonly", font=("Arial", 11))
        self.combo_destino.pack(fill=tk.X, padx=20, pady=5)
        
        btn_calcular = tk.Button(frame, text="🚗 Calcular Rota Mais Rápida", 
                                bg="#00d4ff", fg="black", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2", 
                                command=self.calcular_rota, height=2)
        btn_calcular.pack(fill=tk.X, padx=20, pady=15)
        
        btn_alternativas = tk.Button(frame, text="🗺️ Mostrar 3 Alternativas", 
                                bg="#4caf50", fg="white", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2", 
                                command=self.calcular_alternativas, height=2)
        btn_alternativas.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        resultado_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        tk.Label(resultado_frame, text="📋 Resultado:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=10)
        
        text_frame = tk.Frame(resultado_frame, bg="#0f3460")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_resultado = tk.Text(text_frame, height=10, bg="#1a1a2e", 
                                     fg="white", font=("Consolas", 9),
                                     relief=tk.FLAT, padx=10, pady=10,
                                     yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.text_resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_resultado.yview)
        
        self.text_resultado.insert("1.0", "✨ Sistema Pronto!\n\n📊 Malha 10x10\n🛣️ 100+ interseções\n🚦 Vias de mão única\n🚫 Becos sem saída")
        self.text_resultado.config(state=tk.DISABLED)

    def criar_aba_eventos(self, notebook):
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="⚠️ Eventos")
        
        titulo = tk.Label(frame, text="Eventos de Trânsito", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        info_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(info_frame, text="💡 Como funcionam os eventos:", 
                bg="#0f3460", fg="#00d4ff", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        tk.Label(info_frame, text="💥 Acidente: Reduz velocidade para 10 km/h", 
                bg="#0f3460", fg="#ff4444", font=("Arial", 9)).pack(anchor="w", padx=10)
        tk.Label(info_frame, text="🚧 Obra: Reduz velocidade para 20 km/h", 
                bg="#0f3460", fg="#ff9800", font=("Arial", 9)).pack(anchor="w", padx=10)
        tk.Label(info_frame, text="🚦 Engarrafamento: Reduz velocidade para 30 km/h", 
                bg="#0f3460", fg="#ffeb3b", font=("Arial", 9)).pack(anchor="w", padx=10, pady=(0, 10))
        
        btn_frame = tk.Frame(frame, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_acidente = tk.Button(btn_frame, text="💥\nAcidente", bg="#ff4444", 
                                fg="white", font=("Arial", 10, "bold"),
                                relief=tk.FLAT, cursor="hand2", height=3,
                                command=lambda: self.registrar_evento_dialog('acidente'))
        btn_acidente.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        
        btn_obra = tk.Button(btn_frame, text="🚧\nObra", bg="#ff9800",
                            fg="white", font=("Arial", 10, "bold"),
                            relief=tk.FLAT, cursor="hand2", height=3,
                            command=lambda: self.registrar_evento_dialog('obra'))
        btn_obra.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        
        btn_engarra = tk.Button(btn_frame, text="🚦\nEngarrafamento", bg="#ffeb3b",
                               fg="black", font=("Arial", 10, "bold"),
                               relief=tk.FLAT, cursor="hand2", height=3,
                               command=lambda: self.registrar_evento_dialog('engarrafamento'))
        btn_engarra.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5, 0))
        
        btn_remover = tk.Button(frame, text="🗑️ Remover Evento", bg="#f44336",
                               fg="white", font=("Arial", 10, "bold"),
                               relief=tk.FLAT, cursor="hand2",
                               command=self.remover_evento_dialog)
        btn_remover.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        lista_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(lista_frame, text="📋 Eventos Ativos:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)
        
        self.lista_eventos = tk.Listbox(lista_frame, bg="#1a1a2e", fg="white", 
                                       font=("Consolas", 9), height=5)
        self.lista_eventos.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.atualizar_lista_eventos()

    def criar_aba_estatisticas(self, notebook):
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="📊 Stats")
        
        titulo = tk.Label(frame, text="Estatísticas da Malha", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        stats_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        self.label_total_intersecoes = tk.Label(stats_frame, text="Interseções: 0", 
                                                bg="#0f3460", fg="white", font=("Arial", 10))
        self.label_total_intersecoes.pack(anchor="w", padx=10, pady=5)
        
        self.label_total_vias = tk.Label(stats_frame, text="Vias (Direcionais): 0", 
                                         bg="#0f3460", fg="white", font=("Arial", 10))
        self.label_total_vias.pack(anchor="w", padx=10, pady=5)
        
        self.label_distancia_total = tk.Label(stats_frame, text="Distância Total: 0 km", 
                                              bg="#0f3460", fg="white", font=("Arial", 10))
        self.label_distancia_total.pack(anchor="w", padx=10, pady=5)
        
        self.label_eventos_ativos = tk.Label(stats_frame, text="Eventos Ativos: 0", 
                                             bg="#0f3460", fg="#ff9800", font=("Arial", 10, "bold"))
        self.label_eventos_ativos.pack(anchor="w", padx=10, pady=5)

        btn_atualizar = tk.Button(frame, text="🔄 Atualizar Estatísticas", bg="#2196f3", 
                                fg="white", font=("Arial", 10, "bold"), relief=tk.FLAT, 
                                cursor="hand2", command=self.atualizar_estatisticas)
        btn_atualizar.pack(fill=tk.X, padx=20, pady=15)
        
        self.atualizar_estatisticas()

    def desenhar_grafo(self):
        self.canvas.delete("all")
        if not self.grafo.vertices:
            return
        
        if not self.vertices_pos or self.canvas.winfo_width() == 1:
            self.calcular_layout_grid()
        
        arestas_desenhadas = set() 

        # Desenhar arestas
        for origem, destino, _ in self.grafo.obter_todas_arestas():
            par = tuple(sorted([origem, destino]))
            eh_bidi = self.grafo.obter_peso(destino, origem) is not None
            
            if eh_bidi and par in arestas_desenhadas:
                continue
            
            if eh_bidi:
                arestas_desenhadas.add(par)
            
            if origem not in self.vertices_pos or destino not in self.vertices_pos:
                continue
                
            x1, y1 = self.vertices_pos[origem]
            x2, y2 = self.vertices_pos[destino]
            
            info = self.sistema.obter_info_via(origem, destino)
            if not info: 
                info = self.sistema.obter_info_via(destino, origem)
                if not info: 
                    continue
            
            # Cor e largura
            cor = "#000000"  # PRETO para vias normais
            largura = 2
            
            is_on_main_path = self._is_segment_on_path(origem, destino, self.caminho_atual)
            has_event = info['velocidade_kmh'] < self.sistema.VELOCIDADE_PADRAO
            
            is_on_alt_path = False
            alt_path_index = -1
            for idx, alt_caminho in enumerate(self.caminhos_alternativos):
                 if alt_caminho != self.caminho_atual and self._is_segment_on_path(origem, destino, alt_caminho):
                    is_on_alt_path = True
                    alt_path_index = idx
                    break

            if is_on_main_path:
                cor = "#1E88E5"  # Azul - Rota principal
                largura = 6
            elif is_on_alt_path:
                cores_alt = ["#7CB342", "#FFA726", "#AB47BC"]  # Verde, Laranja, Roxo
                cor = cores_alt[alt_path_index % len(cores_alt)]
                largura = 4
            elif has_event: 
                 cor = "#E53935"  # Vermelho - apenas para eventos
                 largura = 3
            
            self.canvas.create_line(x1, y1, x2, y2, fill=cor, width=largura, capstyle=tk.ROUND)
            
            # Labels de distância/tempo
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            
            if is_on_main_path or is_on_alt_path:
                label_text = f"{info['distancia_km']:.1f}km · {info['tempo_min']:.0f}min"
                
                bbox = self.canvas.create_text(mx, my - 12, text=label_text, 
                                              font=("Arial", 8, "bold"), 
                                              anchor=tk.CENTER, tags=("overlay_temp"))
                
                coords = self.canvas.bbox(bbox)
                if coords:
                    self.canvas.delete(bbox)
                    padding = 3
                    self.canvas.create_rectangle(coords[0]-padding, coords[1]-padding, 
                                                coords[2]+padding, coords[3]+padding,
                                                fill="white", outline=cor, width=2, tags=("overlay"))
                    
                    self.canvas.create_text(mx, my - 12, text=label_text, fill=cor,
                                          font=("Arial", 8, "bold"), anchor=tk.CENTER, tags=("overlay"))
            
            # Setas para mão única
            if not eh_bidi:
                dx, dy = x2 - x1, y2 - y1
                comp = math.sqrt(dx**2 + dy**2)
                if comp > 0:
                    for fator in [0.3, 0.5, 0.7]:
                        mx_arrow = x1 * (1-fator) + x2 * fator
                        my_arrow = y1 * (1-fator) + y2 * fator
                        
                        ux, uy = dx / comp, dy / comp
                        px, py = -uy, ux
                        tam = 8
                        
                        p1 = (mx_arrow + ux * tam, my_arrow + uy * tam)
                        p2 = (mx_arrow - ux * tam/2 + px * tam/2, my_arrow - uy * tam/2 + py * tam/2)
                        p3 = (mx_arrow - ux * tam/2 - px * tam/2, my_arrow - uy * tam/2 - py * tam/2)
                        
                        self.canvas.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
                                                   fill="white", outline=cor, width=1)
        
        # Desenhar vértices
        for vertice, (x, y) in self.vertices_pos.items():
            cor = "#FFFFFF" 
            outline_cor = "#BDBDBD" 
            raio = 8
            
            if self.caminho_atual:
                if vertice == self.caminho_atual[0]:
                    raio = 14
                    self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill="#34A853", outline="white", width=3)
                    self.canvas.create_text(x, y-raio-15, text="🚗 ORIGEM", fill="#34A853", 
                                          font=("Arial", 9, "bold"), anchor=tk.S)
                    continue
                elif vertice == self.caminho_atual[-1]:
                    raio = 14
                    self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill="#EA4335", outline="white", width=3)
                    self.canvas.create_text(x, y-raio-15, text="📍 DESTINO", fill="#EA4335", 
                                          font=("Arial", 9, "bold"), anchor=tk.S)
                    continue
                elif vertice in self.caminho_atual:
                    raio = 6
                    outline_cor = "#1E88E5"
            
            if vertice.startswith('BECO'):
                cor, raio = "#FFEB3B", 10
                outline_cor = "#F57C00"
                self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill=cor, outline=outline_cor, width=2)
                self.canvas.create_text(x, y+raio+10, text="🚫", fill="#F57C00", 
                                      font=("Arial", 10))
                continue
            
            elif vertice.startswith('ISOLADA'):
                cor, raio = "#FFCDD2", 10
                outline_cor = "#E53935"
                self.canvas.create_oval(x-25, y-25, x+25, y+25, outline="#E53935", width=2, dash=(4,4))
                self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill=cor, outline=outline_cor, width=2)
                self.canvas.create_text(x, y-30, text="⚠️", fill="#E53935", font=("Arial", 10))
                continue
            
            self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio, fill=cor, outline=outline_cor, width=1)

    def calcular_layout_grid(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 1000
            canvas_height = 750

        margin = 50
        usable_width = canvas_width - 2 * margin
        usable_height = canvas_height - 2 * margin
        cols, rows = 10, 10
        
        cell_width = usable_width / (cols - 1)
        cell_height = usable_height / (rows - 1)
        
        for vertice in self.grafo.vertices:
            if vertice.startswith('R'):
                try:
                    parts = vertice[1:].split('C')
                    linha = int(parts[0]) - 1 
                    coluna = int(parts[1]) - 1 
                
                    x = margin + coluna * cell_width
                    y = margin + linha * cell_height
                    self.vertices_pos[vertice] = (x, y)
                except:
                     pass
                     
            elif vertice.startswith('BECO'):
                becos_pos = {
                    'BECO1': ('R2C2', 40, -40),
                    'BECO2': ('R4C9', 50, 0),
                    'BECO3': ('R8C2', -40, 40),
                    'BECO4': ('R9C8', 0, 50),
                    'BECO5': ('R6C6', 30, 30)
                }
                if vertice in becos_pos:
                    base_v, ox, oy = becos_pos[vertice]
                    if base_v in self.vertices_pos:
                        base = self.vertices_pos[base_v]
                        self.vertices_pos[vertice] = (base[0] + ox, base[1] + oy)
                    
            elif vertice.startswith('ISOLADA'):
                isoladas_pos = {
                    'ISOLADA1': (canvas_width - margin + 60, margin - 30),
                    'ISOLADA2': (canvas_width - margin + 60, margin + 20),
                    'ISOLADA3': (canvas_width - margin + 110, margin - 30)
                }
                if vertice in isoladas_pos:
                    self.vertices_pos[vertice] = isoladas_pos[vertice]

    def calcular_rota(self):
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        if not origem or not destino or origem == destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino diferentes!")
            return
        
        caminho, info, status = self.sistema.calcular_rota_rapida(origem, destino)
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        if caminho is None:
            self.caminho_atual = []
            self.caminhos_alternativos = []
            self.text_resultado.insert("1.0", f"❌ {status}\n\nNão há rota disponível.")
        else:
            self.caminho_atual = caminho
            self.caminhos_alternativos = [caminho]
            resultado = f"🎯 ROTA MAIS RÁPIDA\n\n"
            resultado += f"{'═' * 40}\n"
            resultado += f"📍 {origem} → {destino}\n"
            resultado += f"{'─' * 40}\n\n"
            resultado += f"📏 Distância: {info['distancia_total_km']:.2f} km\n"
            resultado += f"⏱️  Tempo: {info['tempo_total_min']:.1f} min\n"
            resultado += f"🚗 Velocidade média: {info['velocidade_media_kmh']:.1f} km/h\n\n"
            resultado += f"🛣️  Caminho ({len(caminho)} pontos):\n"
            resultado += f"   {' → '.join(caminho[:8])}"
            if len(caminho) > 8:
                resultado += f"\n   → ... → {caminho[-1]}"
            resultado += f"\n\n💡 Rota em AZUL no mapa!"
            self.text_resultado.insert("1.0", resultado)
        
        self.text_resultado.config(state=tk.DISABLED)
        self.desenhar_grafo()

    def calcular_alternativas(self):
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        if not origem or not destino or origem == destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino diferentes!")
            return
        
        rotas = self.sistema.calcular_k_melhores_rotas(origem, destino, k=3)
        if not rotas:
            messagebox.showerror("Erro", "Não foi possível encontrar rotas!")
            return
        
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        self.caminho_atual = rotas[0]['caminho']
        self.caminhos_alternativos = [r['caminho'] for r in rotas]
        
        resultado = f"🗺️ ATÉ 3 ROTAS DISPONÍVEIS\n\n"
        resultado += f"📍 {origem} ➜ {destino}\n"
        resultado += f"{'═' * 40}\n\n"
        
        icones = ["🔵", "🟢", "🟠"]
        labels = ["MAIS RÁPIDA", "ALTERNATIVA 1", "ALTERNATIVA 2"]
        
        for i, rota in enumerate(rotas):
            info = rota['info']
            caminho = rota['caminho']
            
            resultado += f"{icones[i]} {labels[i]}\n"
            resultado += f"{'─' * 40}\n"
            resultado += f"📏 {info['distancia_total_km']:.1f} km\n"
            resultado += f"⏱️  {info['tempo_total_min']:.1f} min\n"
            resultado += f"🚗 {info['velocidade_media_kmh']:.1f} km/h\n"
            resultado += f"🛣️  {' → '.join(caminho[:5])}"
            if len(caminho) > 5:
                resultado += f" → ... → {caminho[-1]}"
            resultado += f" ({len(caminho)})\n"
            
            if i > 0:
                melhor = rotas[0]['info']
                diff_t = info['tempo_total_min'] - melhor['tempo_total_min']
                diff_d = info['distancia_total_km'] - melhor['distancia_total_km']
                
                resultado += f"\n📊 vs. Principal:\n"
                resultado += f"   ⏰ {'+' if diff_t > 0 else ''}{diff_t:.1f} min\n"
                resultado += f"   📏 {'+' if diff_d > 0 else ''}{diff_d:.1f} km\n"
            
            resultado += "\n"
        
        resultado += f"\n💡 Todas as rotas visíveis no mapa!\n"
        resultado += f"   Azul/Verde/Laranja = Rotas\n"
        resultado += f"   Vermelho = Eventos de trânsito\n"
        
        self.text_resultado.insert("1.0", resultado)
        self.text_resultado.config(state=tk.DISABLED)
        self.desenhar_grafo()
        
    def registrar_evento_dialog(self, tipo):
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        if not origem or not destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        
        sucesso, msg = self.sistema.registrar_evento(tipo, origem, destino)
        if sucesso:
            messagebox.showinfo("Evento Registrado", f"{tipo.upper()} registrado em {origem} → {destino}")
            self.atualizar_interface()
        else:
            messagebox.showerror("Erro", msg)

    def remover_evento_dialog(self):
        eventos = self.sistema.avl.listar_todos()
        if not eventos:
            messagebox.showinfo("Remover Evento", "Não há eventos ativos.")
            return

        evento_id = simpledialog.askinteger("Remover Evento", "ID do evento:")
        
        if evento_id:
            sucesso, msg = self.sistema.remover_evento(evento_id)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Evento #{evento_id} removido!")
                self.atualizar_interface()
            else:
                messagebox.showerror("Erro", msg)

    def atualizar_lista_eventos(self):
        self.lista_eventos.delete(0, tk.END)
        eventos = self.sistema.avl.listar_todos()
        for ev in eventos:
            timestamp_str = datetime.fromtimestamp(ev.timestamp).strftime('%H:%M:%S')
            self.lista_eventos.insert(tk.END, f"#{ev.id} {ev.tipo.upper()} ({timestamp_str}) - {ev.localizacao}")
    
    def atualizar_estatisticas(self):
        stats = self.sistema.estatisticas()
        self.label_total_intersecoes.config(text=f"Interseções: {stats['total_intersecoes']}")
        self.label_total_vias.config(text=f"Vias: {stats['total_vias']}")
        self.label_distancia_total.config(text=f"Distância: {stats['distancia_total_km']:.1f} km")
        self.label_eventos_ativos.config(text=f"Eventos: {stats['eventos_ativos']}")

    def criar_dados_exemplo(self):
        # Malha 10x10
        for linha in range(1, 11):
            for coluna in range(1, 11):
                self.grafo.adicionar_vertice(f"R{linha}C{coluna}")
        
        # Vias horizontais
        for linha in range(1, 11):
            for coluna in range(1, 10):
                self.sistema.adicionar_via(f"R{linha}C{coluna}", f"R{linha}C{coluna+1}", 0.8, 40.0)
        
        # Vias verticais
        for coluna in range(1, 11):
            for linha in range(1, 10):
                self.sistema.adicionar_via(f"R{linha}C{coluna}", f"R{linha+1}C{coluna}", 1.2, 50.0)
        
        # Avenidas principais
        for coluna in range(1, 10):
            self.sistema.adicionar_via(f"R5C{coluna}", f"R5C{coluna+1}", 1.5, 70.0)
        
        for linha in range(1, 10):
            self.sistema.adicionar_via(f"R{linha}C5", f"R{linha+1}C5", 2.0, 70.0)
        
        # Expressas
        self.sistema.adicionar_via('R1C1', 'R5C5', 6.0, 80.0)
        self.sistema.adicionar_via('R1C10', 'R5C5', 6.0, 80.0)
        self.sistema.adicionar_via('R10C1', 'R5C5', 6.0, 80.0)
        self.sistema.adicionar_via('R10C10', 'R5C5', 6.0, 80.0)
        
        # Mão única
        for linha in range(1, 10):
            tempo = self.sistema._calcular_tempo(1.0, 45.0)
            self.grafo.adicionar_aresta_direcionada(f"R{linha}C3", f"R{linha+1}C3", tempo)
            self.sistema.velocidades[f"R{linha}C3-R{linha+1}C3"] = 45.0
            self.sistema.distancias[f"R{linha}C3-R{linha+1}C3"] = 1.0
        
        for linha in range(9, 0, -1):
            tempo = self.sistema._calcular_tempo(1.0, 45.0)
            self.grafo.adicionar_aresta_direcionada(f"R{linha+1}C7", f"R{linha}C7", tempo)
            self.sistema.velocidades[f"R{linha+1}C7-R{linha}C7"] = 45.0
            self.sistema.distancias[f"R{linha+1}C7-R{linha}C7"] = 1.0
        
        # Becos
        becos = [
            ('R2C2', 'BECO1', 0.3, 20.0),
            ('R4C9', 'BECO2', 0.4, 20.0),
            ('R8C2', 'BECO3', 0.3, 20.0),
            ('R9C8', 'BECO4', 0.5, 20.0),
            ('R6C6', 'BECO5', 0.2, 15.0),
        ]
        
        for origem, beco, dist, vel in becos:
            self.grafo.adicionar_vertice(beco)
            self.sistema.adicionar_via(origem, beco, dist, vel)
        
        # Isoladas
        for i in range(1, 4):
            self.grafo.adicionar_vertice(f'ISOLADA{i}')
        
        self.sistema.adicionar_via('ISOLADA1', 'ISOLADA2', 0.5, 30.0)
        
        self.atualizar_interface()
        
    def atualizar_interface(self):
        vertices = sorted(list(self.grafo.vertices))
        self.combo_origem['values'] = vertices
        self.combo_destino['values'] = vertices
        self.desenhar_grafo()
        self.atualizar_lista_eventos()
        self.atualizar_estatisticas()

    def mostrar_como_funciona(self):
        msg = """🗺️ SISTEMA DE TRÂNSITO INTELIGENTE PRO

📊 CARACTERÍSTICAS:
• Malha 10x10 (100+ interseções)
• Vias de mão única
• Becos sem saída
• Áreas isoladas
• Eventos em tempo real

🎯 COMO USAR:
1. Selecione origem e destino
2. "Calcular Rota" = melhor opção
3. "Mostrar 3 Alternativas" = todas as rotas

🎨 CORES:
🔵 Azul = Rota principal
🟢 Verde = Alternativa 1
🟠 Laranja = Alternativa 2
🔴 Vermelho = Via com evento
➡️ Setas = Mão única"""
        
        messagebox.showinfo("Como Funciona", msg)


def main():
    root = tk.Tk()
    app = InterfaceTransitoMelhorada(root)
    root.mainloop()


if __name__ == "__main__":
    main()
