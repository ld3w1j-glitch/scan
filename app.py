from __future__ import annotations

import csv
import io
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Any

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db_path() -> str:
    custom_db_path = os.environ.get("DB_PATH", "").strip()
    if custom_db_path:
        return custom_db_path

    volume_mount = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "").strip()
    if volume_mount:
        return os.path.join(volume_mount, "dados.db")

    return os.path.join(BASE_DIR, "dados.db")


DB_PATH = get_db_path()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "alvorada-padaria-loja5")


HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#6cbc55">
  <title>Controle Loja 5</title>
  <style>
    :root {
      --verde: #6cbc55;
      --verde-escuro: #4a8e39;
      --laranja: #f28d16;
      --laranja-escuro: #df7410;
      --cinza-bg: #efefef;
      --cinza-bloco: #f7f7f7;
      --texto: #333333;
      --muted: #747474;
      --borda: #e3e3e3;
      --branco: #ffffff;
      --sombra: 0 14px 32px rgba(0, 0, 0, 0.08);
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--texto);
      background: var(--cinza-bg);
    }
    a { color: inherit; }
    img { max-width: 100%; display: block; }

    .page-shell {
      min-height: 100vh;
      background:
        linear-gradient(180deg, #f9f9f9 0px, #f9f9f9 96px, var(--cinza-bg) 96px, var(--cinza-bg) 100%);
    }

    .header {
      position: sticky;
      top: 0;
      z-index: 30;
      background: rgba(255,255,255,.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(0,0,0,.05);
    }

    .header-inner,
    .container {
      width: min(1220px, calc(100vw - 24px));
      margin: 0 auto;
    }

    .header-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      min-height: 96px;
      padding: 14px 0;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .brand img {
      width: 118px;
      height: auto;
      object-fit: contain;
    }

    .brand-copy {
      display: none;
    }

    .nav-wrap {
      display: flex;
      align-items: center;
      gap: 16px;
      min-width: 0;
      flex: 1;
      justify-content: flex-end;
    }

    .nav {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      scrollbar-width: none;
      padding-bottom: 4px;
    }
    .nav::-webkit-scrollbar { display: none; }

    .nav a {
      text-decoration: none;
      color: #626262;
      font-size: 15px;
      white-space: nowrap;
      padding: 10px 12px;
      border-radius: 999px;
      transition: .18s ease;
    }
    .nav a:hover {
      background: rgba(108,188,85,.10);
      color: var(--verde-escuro);
    }

    .nav-cta {
      background: var(--laranja);
      color: #111;
      font-weight: 700;
      text-decoration: none;
      padding: 14px 18px;
      border-radius: 0;
      white-space: nowrap;
      box-shadow: 0 8px 18px rgba(242,141,22,.24);
    }

    .container {
      padding: 26px 0 92px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.05fr .95fr;
      gap: 28px;
      align-items: center;
      background: transparent;
      margin-bottom: 28px;
    }

    .hero-copy {
      background: transparent;
      padding: 18px 12px 18px 18px;
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,.8);
      border: 1px solid rgba(108,188,85,.15);
      color: var(--verde-escuro);
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 20px;
      box-shadow: var(--sombra);
    }

    .hero-title {
      line-height: .88;
      margin: 0;
      color: var(--verde);
      letter-spacing: -2px;
      font-weight: 800;
    }
    .hero-title .big {
      display: block;
      font-size: clamp(76px, 13vw, 142px);
    }
    .hero-title .small {
      display: block;
      font-size: clamp(40px, 6.6vw, 78px);
    }

    .hero-subtitle {
      max-width: 520px;
      color: var(--laranja);
      font-size: clamp(22px, 2.5vw, 44px);
      line-height: 1.25;
      margin: 26px 0 22px;
      font-weight: 300;
    }

    .hero-text {
      max-width: 580px;
      color: #696969;
      font-size: 16px;
      line-height: 1.7;
      margin-bottom: 24px;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 24px;
    }

    .btn,
    button,
    input,
    select {
      font: inherit;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 56px;
      border: none;
      border-radius: 0;
      text-decoration: none;
      padding: 0 22px;
      cursor: pointer;
      transition: .18s ease;
      width: auto;
      font-weight: 700;
    }

    .btn-primary {
      background: var(--laranja);
      color: #fff;
      box-shadow: 0 14px 28px rgba(242,141,22,.22);
    }
    .btn-primary:hover { background: var(--laranja-escuro); }

    .btn-secondary {
      background: #ffffff;
      color: var(--texto);
      border: 1px solid var(--borda);
    }

    .summary-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }

    .metric {
      background: rgba(255,255,255,.78);
      border: 1px solid rgba(0,0,0,.04);
      border-radius: 16px;
      padding: 14px 16px;
      box-shadow: var(--sombra);
      min-height: 92px;
    }
    .metric span {
      display: block;
      font-size: 12px;
      color: #6d6d6d;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    .metric strong {
      display: block;
      font-size: clamp(22px, 3vw, 34px);
      color: var(--verde-escuro);
      line-height: 1;
    }

    .hero-media {
      position: relative;
    }

    .hero-photo-card {
      position: relative;
      border-radius: 8px;
      overflow: hidden;
      background: white;
      box-shadow: 0 24px 40px rgba(0,0,0,.14);
      margin-left: auto;
      width: min(100%, 560px);
      border-bottom: 6px solid var(--verde);
    }

    .hero-photo-card img {
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
    }

    .hero-floating {
      position: absolute;
      right: 16px;
      bottom: 16px;
      background: rgba(255,255,255,.94);
      border-radius: 16px;
      padding: 14px 16px;
      box-shadow: 0 14px 28px rgba(0,0,0,.12);
      min-width: 200px;
      border-left: 6px solid var(--laranja);
    }
    .hero-floating small {
      display: block;
      color: #7a7a7a;
      margin-bottom: 6px;
    }
    .hero-floating strong {
      font-size: 18px;
      color: var(--texto);
    }

    .main-grid {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 22px;
      align-items: start;
    }

    .card {
      background: rgba(255,255,255,.9);
      border: 1px solid rgba(0,0,0,.05);
      border-radius: var(--radius-xl);
      box-shadow: var(--sombra);
      padding: 24px;
    }

    .card-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 18px;
    }

    .card h2,
    .card h3,
    .card p {
      margin-top: 0;
    }

    .section-label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(108,188,85,.12);
      color: var(--verde-escuro);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .05em;
      margin-bottom: 12px;
    }

    .subtitle {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 0;
    }

    .flash {
      background: rgba(108,188,85,.12);
      color: #2d5f22;
      border: 1px solid rgba(108,188,85,.24);
      padding: 14px 16px;
      border-radius: 16px;
      margin-bottom: 18px;
      box-shadow: var(--sombra);
    }
    .flash.error {
      background: rgba(219,77,77,.10);
      color: #9c2d2d;
      border-color: rgba(219,77,77,.22);
    }

    .field { margin-bottom: 14px; }
    label {
      display: block;
      font-size: 13px;
      color: #666;
      margin-bottom: 7px;
      font-weight: 700;
    }

    input,
    select {
      width: 100%;
      min-height: 54px;
      border: 1px solid #dddddd;
      background: #ffffff;
      color: var(--texto);
      padding: 14px 16px;
      border-radius: 14px;
      outline: none;
      transition: .18s ease;
    }
    input:focus,
    select:focus {
      border-color: rgba(108,188,85,.6);
      box-shadow: 0 0 0 4px rgba(108,188,85,.14);
    }

    .btn-block {
      width: 100%;
      min-height: 54px;
      border-radius: 14px;
    }

    .btn-row,
    .btn-row-2 {
      display: grid;
      gap: 10px;
      margin-bottom: 6px;
    }
    .btn-row { grid-template-columns: 1fr 1fr; }
    .btn-row-2 { grid-template-columns: 1fr 1fr; }

    .upload-label {
      min-height: 54px;
      border: 1px solid var(--borda);
      background: #fff;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      cursor: pointer;
      padding: 0 12px;
    }
    .upload-label input { display: none; }

    .help {
      color: #7a7a7a;
      font-size: 13px;
      line-height: 1.55;
      margin: 8px 0 0;
    }

    .radio-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .radio-card {
      position: relative;
    }
    .radio-card input {
      position: absolute;
      opacity: 0;
      inset: 0;
    }
    .radio-card label {
      min-height: 58px;
      margin: 0;
      border: 1px solid var(--borda);
      background: white;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      color: #5a5a5a;
      cursor: pointer;
      transition: .18s ease;
    }
    .radio-card input:checked + label {
      background: rgba(108,188,85,.12);
      border-color: rgba(108,188,85,.45);
      color: var(--verde-escuro);
    }

    .inventory-panel {
      border-top: 1px solid var(--borda);
      margin-top: 22px;
      padding-top: 18px;
    }

    .card-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
    }

    .card-actions .btn {
      border-radius: 14px;
      min-height: 52px;
    }

    .desktop-table {
      display: block;
    }

    .table-wrap {
      overflow: auto;
      border: 1px solid var(--borda);
      border-radius: 18px;
      background: white;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
    }

    th,
    td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--borda);
      text-align: left;
      font-size: 14px;
      vertical-align: top;
    }
    th {
      background: #f8f8f8;
      color: #636363;
      text-transform: uppercase;
      letter-spacing: .03em;
      font-size: 12px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }
    .tag-loja {
      background: rgba(242,141,22,.14);
      color: #b75f00;
    }
    .tag-estoque {
      background: rgba(108,188,85,.14);
      color: #3d7b2c;
    }

    .mobile-list {
      display: none;
      gap: 12px;
    }

    .mobile-row {
      border: 1px solid var(--borda);
      border-radius: 18px;
      background: white;
      padding: 14px;
    }

    .mobile-row-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .mobile-row h4 {
      margin: 0 0 6px;
      font-size: 16px;
    }

    .mobile-meta {
      display: grid;
      gap: 8px;
      font-size: 13px;
      color: #626262;
    }

    .recent-list {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }

    .recent-item {
      border: 1px solid var(--borda);
      border-radius: 18px;
      background: #fbfbfb;
      padding: 14px 16px;
    }
    .recent-item strong {
      display: block;
      margin-bottom: 8px;
    }

    .recent-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }

    .inline-form {
      margin: 0;
    }

    .btn-small {
      min-height: 40px;
      padding: 0 14px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 700;
    }

    .btn-danger {
      background: #fff4f4;
      color: #9c2d2d;
      border: 1px solid #efc1c1;
    }
    .btn-danger:hover {
      background: #ffeaea;
    }

    .muted { color: var(--muted); }

    .scanner-modal {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,.58);
      padding: 18px;
      z-index: 100;
    }

    .scanner-box {
      width: min(580px, 100%);
      background: white;
      border-radius: 26px;
      padding: 18px;
      box-shadow: 0 24px 48px rgba(0,0,0,.22);
    }

    .scanner-box video {
      width: 100%;
      border-radius: 18px;
      background: #000;
      min-height: 240px;
      object-fit: cover;
    }

    .mobile-bar {
      display: none;
      position: fixed;
      left: 10px;
      right: 10px;
      bottom: 10px;
      z-index: 25;
      background: rgba(255,255,255,.95);
      border: 1px solid rgba(0,0,0,.06);
      box-shadow: 0 18px 34px rgba(0,0,0,.12);
      border-radius: 18px;
      padding: 10px;
      gap: 10px;
    }

    .mobile-bar .btn {
      flex: 1;
      min-height: 48px;
      border-radius: 12px;
      font-size: 14px;
      padding: 0 12px;
    }

    @media (max-width: 1100px) {
      .hero {
        grid-template-columns: 1fr;
      }

      .main-grid {
        grid-template-columns: 1fr;
      }

      .hero-copy {
        order: 2;
        padding: 0;
      }

      .hero-media {
        order: 1;
      }

      .hero-photo-card {
        width: 100%;
      }

      .summary-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 780px) {
      .page-shell {
        background: linear-gradient(180deg, #f9f9f9 0px, #f9f9f9 84px, var(--cinza-bg) 84px, var(--cinza-bg) 100%);
      }

      .header-inner {
        min-height: 84px;
        padding: 10px 0;
        align-items: center;
      }

      .brand img {
        width: 96px;
      }

      .nav-wrap {
        gap: 10px;
      }

      .nav {
        max-width: 100%;
      }

      .nav a {
        font-size: 13px;
        padding: 8px 10px;
      }

      .nav-cta {
        display: none;
      }

      .container {
        width: min(100vw - 16px, 1220px);
        padding-top: 18px;
      }

      .hero {
        gap: 16px;
        margin-bottom: 20px;
      }

      .hero-photo-card {
        border-radius: 20px;
      }

      .hero-floating {
        position: static;
        margin-top: 12px;
      }

      .hero-subtitle {
        font-size: 22px;
        margin: 18px 0 14px;
      }

      .hero-text {
        font-size: 14px;
        margin-bottom: 18px;
      }

      .hero-actions,
      .card-actions,
      .btn-row,
      .btn-row-2,
      .radio-group {
        grid-template-columns: 1fr;
        display: grid;
      }

      .hero-actions .btn,
      .card-actions .btn,
      .btn,
      .upload-label {
        width: 100%;
      }

      .summary-strip {
        grid-template-columns: 1fr 1fr;
      }

      .metric {
        min-height: 84px;
        border-radius: 14px;
      }

      .card {
        border-radius: 22px;
        padding: 18px;
      }

      .desktop-table {
        display: none;
      }

      .mobile-list {
        display: grid;
      }

      .mobile-bar {
        display: flex;
      }
    }

    @media (max-width: 480px) {
      .hero-title .big { font-size: 76px; }
      .hero-title .small { font-size: 42px; }
      .summary-strip { grid-template-columns: 1fr; }
      .header-inner { gap: 10px; }
      .brand img { width: 84px; }
      .nav a { font-size: 12px; padding: 7px 9px; }
    }
  </style>
</head>
<body>
  <div class="page-shell">
    <header class="header">
      <div class="header-inner">
        <div class="brand">
          <img src="{{ url_for('static', filename='logo_alvorada.png') }}" alt="Supermercados Alvorada">
        </div>

        <div class="nav-wrap">
          <nav class="nav">
            <a href="#inicio">Rede Alvorada</a>
            <a href="#cadastro">Levantamento</a>
            <a href="#relatorio">Relatório</a>
            <a href="#inventarios">Inventários</a>
            <a href="{{ url_for('relatorio_impressao') }}" target="_blank">Impressão</a>
          </nav>
          <a class="nav-cta" href="#cadastro">Registrar Mercadoria</a>
        </div>
      </div>
    </header>

    <main class="container" id="inicio">
      {% if mensagem %}
        <div class="flash {% if erro %}error{% endif %}">{{ mensagem }}</div>
      {% endif %}

      <section class="hero">
        <div class="hero-copy">
          <span class="hero-badge">Centro de Distribuição · Padaria · Inventário ativo: {{ inventario['nome'] }}</span>
          <h1 class="hero-title">
            <span class="big">LOJA 5</span>
            <span class="small">LEVANTAMENTO</span>
          </h1>
          <p class="hero-subtitle">Para separar com clareza o que é do estoque e o que chegou da Loja 5.</p>
          <p class="hero-text">
            Use a câmera do celular ou digite o código manualmente, informe o produto e a quantidade, e gere o relatório final no mesmo estilo limpo e direto.
          </p>

          <div class="hero-actions">
            <a class="btn btn-primary" href="#cadastro">Começar registro</a>
            <a class="btn btn-secondary" href="#relatorio">Ver relatório parcial</a>
          </div>

          <div class="summary-strip">
            <div class="metric">
              <span>Linhas agrupadas</span>
              <strong>{{ resumo.total_linhas }}</strong>
            </div>
            <div class="metric">
              <span>Quantidade total</span>
              <strong>{{ resumo.total_quantidade }}</strong>
            </div>
            <div class="metric">
              <span>Estoque</span>
              <strong>{{ resumo.total_estoque }}</strong>
            </div>
            <div class="metric">
              <span>Loja 5</span>
              <strong>{{ resumo.total_loja5 }}</strong>
            </div>
          </div>
        </div>

        <div class="hero-media">
          <div class="hero-photo-card">
            <img src="{{ url_for('static', filename='hero_loja.jpg') }}" alt="Loja Alvorada">
          </div>
          <div class="hero-floating">
            <small>Status do trabalho</small>
            <strong>Leitura rápida no celular + relatório para imprimir</strong>
          </div>
        </div>
      </section>

      <section class="main-grid">
        <div class="card" id="cadastro">
          <span class="section-label">Cadastro de mercadoria</span>
          <div class="card-header">
            <div>
              <h2>Registrar item</h2>
              <p class="subtitle">Escaneie o código, informe nome e quantidade e marque a origem correta.</p>
            </div>
          </div>

          <form method="post" action="{{ url_for('adicionar_item') }}">
            <div class="field">
              <label for="codigo_barras">Código de barras</label>
              <input id="codigo_barras" name="codigo_barras" placeholder="Escaneie ou digite o código" autocomplete="off" required>
            </div>

            <div class="btn-row">
              <button type="button" class="btn btn-secondary btn-block" onclick="abrirScanner()">Ler pela câmera</button>
              <label class="upload-label">
                Ler por foto
                <input id="foto_codigo" type="file" accept="image/*" capture="environment">
              </label>
            </div>
            <p class="help">No celular, a câmera costuma funcionar melhor pelo navegador Chrome. Se não abrir, digite manualmente.</p>

            <div class="field" style="margin-top: 14px;">
              <label for="nome_produto">Nome do produto</label>
              <input id="nome_produto" name="nome_produto" placeholder="Ex.: farinha de trigo, leite, biscoito" required>
            </div>

            <div class="field">
              <label for="quantidade">Quantidade</label>
              <input id="quantidade" name="quantidade" type="number" step="0.001" min="0.001" placeholder="Ex.: 1, 2, 10, 0.5" required>
            </div>

            <div class="field">
              <label>Origem</label>
              <div class="radio-group">
                <div class="radio-card">
                  <input id="origem_estoque" type="radio" name="origem" value="ESTOQUE" required>
                  <label for="origem_estoque">Estoque</label>
                </div>
                <div class="radio-card">
                  <input id="origem_loja5" type="radio" name="origem" value="LOJA 5" checked required>
                  <label for="origem_loja5">Loja 5</label>
                </div>
              </div>
            </div>

            <button class="btn btn-primary btn-block" type="submit">Salvar item</button>
          </form>

          <div class="inventory-panel" id="inventarios">
            <span class="section-label">Inventários</span>
            <h3>Trocar ou criar inventário</h3>

            <form method="post" action="{{ url_for('selecionar_inventario') }}">
              <div class="field">
                <label for="inventario_id">Inventários existentes</label>
                <select id="inventario_id" name="inventario_id">
                  {% for item in inventarios %}
                    <option value="{{ item['id'] }}" {% if item['id'] == inventario['id'] %}selected{% endif %}>{{ item['nome'] }}</option>
                  {% endfor %}
                </select>
              </div>
              <button class="btn btn-secondary btn-block" type="submit">Usar este inventário</button>
            </form>

            <form method="post" action="{{ url_for('novo_inventario') }}" style="margin-top: 12px;">
              <div class="field">
                <label for="nome_inventario">Criar novo inventário</label>
                <input id="nome_inventario" name="nome_inventario" placeholder="Ex.: Incêndio Loja 5 - Abril 2026" required>
              </div>
              <button class="btn btn-primary btn-block" type="submit">Criar novo inventário</button>
            </form>

            <form method="post" action="{{ url_for('limpar_inventario_atual') }}" style="margin-top: 12px;" onsubmit="return confirm('Tem certeza que deseja apagar TODOS os registros do inventário atual?');">
              <button class="btn btn-secondary btn-block" type="submit" style="border-color:#efc1c1;color:#9c2d2d;background:#fff4f4;">Apagar tudo deste inventário</button>
            </form>
          </div>
        </div>

        <div class="card" id="relatorio">
          <span class="section-label">Relatório parcial</span>
          <div class="card-header">
            <div>
              <h2>Produtos registrados</h2>
              <p class="subtitle">Os itens abaixo já aparecem agrupados por código, produto e origem.</p>
            </div>
          </div>

          <div class="card-actions">
            <a class="btn btn-primary" href="{{ url_for('exportar_csv') }}">Baixar CSV</a>
            <a class="btn btn-secondary" href="{{ url_for('relatorio_impressao') }}" target="_blank">Abrir para imprimir</a>
          </div>

          <div class="desktop-table">
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Produto</th>
                    <th>Origem</th>
                    <th>Quantidade</th>
                  </tr>
                </thead>
                <tbody>
                  {% if agrupados %}
                    {% for row in agrupados %}
                      <tr>
                        <td>{{ row['codigo_barras'] }}</td>
                        <td>{{ row['nome_produto'] }}</td>
                        <td>
                          {% if row['origem'] == 'LOJA 5' %}
                            <span class="tag tag-loja">Loja 5</span>
                          {% else %}
                            <span class="tag tag-estoque">Estoque</span>
                          {% endif %}
                        </td>
                        <td>{{ row['quantidade_total'] }}</td>
                      </tr>
                    {% endfor %}
                  {% else %}
                    <tr>
                      <td colspan="4" class="muted">Nenhum item registrado ainda.</td>
                    </tr>
                  {% endif %}
                </tbody>
              </table>
            </div>
          </div>

          <div class="mobile-list">
            {% if agrupados %}
              {% for row in agrupados %}
                <article class="mobile-row">
                  <div class="mobile-row-top">
                    <div>
                      <h4>{{ row['nome_produto'] }}</h4>
                      <div class="muted">Código: {{ row['codigo_barras'] }}</div>
                    </div>
                    <div>
                      {% if row['origem'] == 'LOJA 5' %}
                        <span class="tag tag-loja">Loja 5</span>
                      {% else %}
                        <span class="tag tag-estoque">Estoque</span>
                      {% endif %}
                    </div>
                  </div>
                  <div class="mobile-meta">
                    <div><strong>Quantidade:</strong> {{ row['quantidade_total'] }}</div>
                  </div>
                </article>
              {% endfor %}
            {% else %}
              <article class="mobile-row muted">Nenhum item registrado ainda.</article>
            {% endif %}
          </div>

          <h3 style="margin-top: 22px;">Lançamentos individuais</h3>
          <p class="subtitle" style="margin-bottom:16px;">Se você lançar algo errado, pode editar ou excluir o registro individual abaixo.</p>
          <div class="recent-list">
            {% if recentes %}
              {% for row in recentes %}
                <div class="recent-item">
                  <strong>{{ row['nome_produto'] }}</strong>
                  <div class="muted">Código: {{ row['codigo_barras'] }}</div>
                  <div class="muted">Origem: {{ row['origem'] }} · Quantidade: {{ row['quantidade'] }}</div>
                  <div class="muted">{{ row['criado_em'] }}</div>
                  <div class="recent-actions">
                    <a class="btn btn-secondary btn-small" href="{{ url_for('editar_item', registro_id=row['id']) }}">Editar</a>
                    <form class="inline-form" method="post" action="{{ url_for('excluir_item', registro_id=row['id']) }}" onsubmit="return confirm('Tem certeza que deseja excluir este lançamento?');">
                      <button class="btn btn-danger btn-small" type="submit">Excluir</button>
                    </form>
                  </div>
                </div>
              {% endfor %}
            {% else %}
              <div class="recent-item muted">Sem lançamentos até agora.</div>
            {% endif %}
          </div>
        </div>
      </section>
    </main>
  </div>

  <div class="scanner-modal" id="scannerModal">
    <div class="scanner-box">
      <div class="card-header" style="margin-bottom: 12px;">
        <div>
          <h3 style="margin-bottom: 6px;">Ler código de barras</h3>
          <p class="subtitle">Aponte a câmera para o código.</p>
        </div>
        <button type="button" class="btn btn-secondary" style="min-height: 44px; border-radius: 12px;" onclick="fecharScanner()">Fechar</button>
      </div>
      <video id="video" autoplay playsinline></video>
      <p id="scanStatus" class="help">Abrindo câmera...</p>
    </div>
  </div>

  <div class="mobile-bar">
    <a class="btn btn-secondary" href="#relatorio">Relatório</a>
    <a class="btn btn-primary" href="#cadastro">Cadastrar</a>
  </div>

  <script>
    const codigoInput = document.getElementById('codigo_barras');
    const nomeInput = document.getElementById('nome_produto');
    const fotoCodigo = document.getElementById('foto_codigo');
    const scannerModal = document.getElementById('scannerModal');
    const video = document.getElementById('video');
    const scanStatus = document.getElementById('scanStatus');

    let stream = null;
    let timer = null;
    let detector = null;

    async function preencherNomePorCodigo() {
      const codigo = codigoInput.value.trim();
      if (!codigo) return;
      try {
        const resp = await fetch(`/buscar_produto?codigo=${encodeURIComponent(codigo)}`);
        const data = await resp.json();
        if (data && data.nome_produto && !nomeInput.value.trim()) {
          nomeInput.value = data.nome_produto;
        }
      } catch (e) {
        console.log('Falha ao buscar nome do produto:', e);
      }
    }

    codigoInput.addEventListener('change', preencherNomePorCodigo);
    codigoInput.addEventListener('blur', preencherNomePorCodigo);

    async function abrirScanner() {
      scannerModal.style.display = 'flex';
      scanStatus.textContent = 'Abrindo câmera...';

      if (!('BarcodeDetector' in window)) {
        scanStatus.textContent = 'Seu navegador não suporta leitura automática aqui. Use foto ou digite manualmente.';
        return;
      }

      try {
        const formatos = await BarcodeDetector.getSupportedFormats();
        const preferidos = ['ean_13', 'ean_8', 'code_128', 'upc_a', 'upc_e', 'code_39', 'codabar'];
        const ativos = preferidos.filter(f => formatos.includes(f));
        detector = new BarcodeDetector({ formats: ativos.length ? ativos : formatos });

        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: 'environment' } },
          audio: false,
        });
        video.srcObject = stream;
        scanStatus.textContent = 'Aponte para o código de barras.';

        timer = setInterval(async () => {
          try {
            const resultados = await detector.detect(video);
            if (resultados.length) {
              const valor = resultados[0].rawValue || '';
              if (valor) {
                codigoInput.value = valor;
                await preencherNomePorCodigo();
                fecharScanner();
                document.getElementById('nome_produto').focus();
              }
            }
          } catch (err) {
            console.log(err);
          }
        }, 550);
      } catch (err) {
        scanStatus.textContent = 'Não foi possível usar a câmera neste navegador. Use a foto ou digite manualmente.';
        console.log(err);
      }
    }

    function fecharScanner() {
      scannerModal.style.display = 'none';
      if (timer) clearInterval(timer);
      timer = null;
      if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
      }
      video.srcObject = null;
    }

    fotoCodigo.addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      if (!('BarcodeDetector' in window)) {
        alert('Seu navegador não suporta leitura automática por imagem aqui. Digite o código manualmente.');
        return;
      }

      try {
        const formatos = await BarcodeDetector.getSupportedFormats();
        detector = new BarcodeDetector({ formats });
        const bitmap = await createImageBitmap(file);
        const resultados = await detector.detect(bitmap);
        if (resultados.length) {
          codigoInput.value = resultados[0].rawValue || '';
          await preencherNomePorCodigo();
          document.getElementById('nome_produto').focus();
        } else {
          alert('Nenhum código detectado na imagem.');
        }
      } catch (err) {
        console.log(err);
        alert('Falha ao ler a imagem. Você pode digitar o código manualmente.');
      } finally {
        fotoCodigo.value = '';
      }
    });
  </script>
</body>
</html>
"""


HTML_PRINT = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relatório - {{ inventario['nome'] }}</title>
  <style>
    body {
      font-family: Arial, Helvetica, sans-serif;
      margin: 24px;
      color: #222;
      background: #f7f7f7;
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
      background: white;
      border: 1px solid #e7e7e7;
      border-radius: 18px;
      padding: 24px;
    }
    .top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      border-bottom: 1px solid #ececec;
      padding-bottom: 18px;
      margin-bottom: 18px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand img { width: 108px; }
    h1, h2, p { margin-top: 0; }
    .meta { color: #666; }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .box {
      border: 1px solid #e5e5e5;
      border-radius: 14px;
      padding: 14px;
      background: #fafafa;
    }
    .box span {
      display: block;
      font-size: 12px;
      text-transform: uppercase;
      color: #777;
      margin-bottom: 6px;
    }
    .box strong {
      display: block;
      font-size: 28px;
      color: #4a8e39;
    }
    .print-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
      padding: 0 18px;
      background: #f28d16;
      color: white;
      border: none;
      border-radius: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: white;
    }
    th, td {
      border: 1px solid #e7e7e7;
      padding: 11px 12px;
      text-align: left;
      font-size: 14px;
    }
    th {
      background: #f8f8f8;
      color: #666;
      text-transform: uppercase;
      font-size: 12px;
    }
    @media (max-width: 760px) {
      body { margin: 12px; }
      .wrap { padding: 16px; }
      .top { flex-direction: column; align-items: flex-start; }
      .summary { grid-template-columns: 1fr 1fr; }
    }
    @media print {
      body { margin: 0; background: white; }
      .wrap { border: none; box-shadow: none; }
      .print-btn { display: none; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <div class="brand">
        <img src="{{ url_for('static', filename='logo_alvorada.png') }}" alt="Supermercados Alvorada">
        <div>
          <h1>Relatório de mercadorias</h1>
          <div class="meta">
            <div><strong>Inventário:</strong> {{ inventario['nome'] }}</div>
            <div><strong>Emitido em:</strong> {{ emitido_em }}</div>
          </div>
        </div>
      </div>
      <button class="print-btn" onclick="window.print()">Imprimir / Salvar em PDF</button>
    </div>

    <div class="summary">
      <div class="box"><span>Linhas agrupadas</span><strong>{{ resumo.total_linhas }}</strong></div>
      <div class="box"><span>Quantidade total</span><strong>{{ resumo.total_quantidade }}</strong></div>
      <div class="box"><span>Estoque</span><strong>{{ resumo.total_estoque }}</strong></div>
      <div class="box"><span>Loja 5</span><strong>{{ resumo.total_loja5 }}</strong></div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Código</th>
          <th>Produto</th>
          <th>Origem</th>
          <th>Quantidade</th>
        </tr>
      </thead>
      <tbody>
        {% for row in agrupados %}
        <tr>
          <td>{{ row['codigo_barras'] }}</td>
          <td>{{ row['nome_produto'] }}</td>
          <td>{{ row['origem'] }}</td>
          <td>{{ row['quantidade_total'] }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


HTML_EDIT = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Editar lançamento</title>
  <style>
    :root {
      --verde: #6cbc55;
      --verde-escuro: #4a8e39;
      --laranja: #f28d16;
      --cinza-bg: #efefef;
      --texto: #333333;
      --muted: #747474;
      --borda: #e3e3e3;
      --sombra: 0 14px 32px rgba(0, 0, 0, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--cinza-bg);
      color: var(--texto);
    }
    .wrap {
      width: min(720px, calc(100vw - 20px));
      margin: 24px auto;
    }
    .card {
      background: rgba(255,255,255,.96);
      border: 1px solid rgba(0,0,0,.05);
      border-radius: 28px;
      box-shadow: var(--sombra);
      padding: 22px;
    }
    .label {
      display: inline-flex;
      align-items: center;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(108,188,85,.12);
      color: var(--verde-escuro);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .05em;
      margin-bottom: 12px;
    }
    h1 { margin: 0 0 10px; }
    p { color: var(--muted); line-height: 1.6; }
    .field { margin-bottom: 14px; }
    label {
      display: block;
      font-size: 13px;
      color: #666;
      margin-bottom: 7px;
      font-weight: 700;
    }
    input {
      width: 100%;
      min-height: 54px;
      border: 1px solid #dddddd;
      background: #ffffff;
      color: var(--texto);
      padding: 14px 16px;
      border-radius: 14px;
      outline: none;
    }
    input:focus {
      border-color: rgba(108,188,85,.6);
      box-shadow: 0 0 0 4px rgba(108,188,85,.14);
    }
    .radio-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .radio-card { position: relative; }
    .radio-card input {
      position: absolute;
      opacity: 0;
      inset: 0;
    }
    .radio-card label {
      min-height: 58px;
      margin: 0;
      border: 1px solid var(--borda);
      background: white;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      color: #5a5a5a;
      cursor: pointer;
    }
    .radio-card input:checked + label {
      background: rgba(108,188,85,.12);
      border-color: rgba(108,188,85,.45);
      color: var(--verde-escuro);
    }
    .actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 12px;
    }
    .btn {
      min-height: 54px;
      border: none;
      border-radius: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      font-weight: 700;
      cursor: pointer;
      padding: 0 18px;
      font: inherit;
    }
    .btn-primary { background: var(--laranja); color: white; }
    .btn-secondary { background: white; color: var(--texto); border: 1px solid var(--borda); }
    @media (max-width: 620px) {
      .wrap { margin: 12px auto; }
      .card { border-radius: 22px; padding: 18px; }
      .actions, .radio-group { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <span class="label">Editar lançamento</span>
      <h1>Corrigir item lançado</h1>
      <p>Altere os dados abaixo e salve. Se preferir, volte sem mexer em nada.</p>

      <form method="post">
        <div class="field">
          <label for="codigo_barras">Código de barras</label>
          <input id="codigo_barras" name="codigo_barras" value="{{ registro['codigo_barras'] }}" required>
        </div>

        <div class="field">
          <label for="nome_produto">Nome do produto</label>
          <input id="nome_produto" name="nome_produto" value="{{ registro['nome_produto'] }}" required>
        </div>

        <div class="field">
          <label for="quantidade">Quantidade</label>
          <input id="quantidade" name="quantidade" type="number" step="0.001" min="0.001" value="{{ registro['quantidade'] }}" required>
        </div>

        <div class="field">
          <label>Origem</label>
          <div class="radio-group">
            <div class="radio-card">
              <input id="origem_estoque" type="radio" name="origem" value="ESTOQUE" {% if registro['origem'] == 'ESTOQUE' %}checked{% endif %} required>
              <label for="origem_estoque">Estoque</label>
            </div>
            <div class="radio-card">
              <input id="origem_loja5" type="radio" name="origem" value="LOJA 5" {% if registro['origem'] == 'LOJA 5' %}checked{% endif %} required>
              <label for="origem_loja5">Loja 5</label>
            </div>
          </div>
        </div>

        <div class="actions">
          <a class="btn btn-secondary" href="{{ url_for('index') }}#relatorio">Cancelar</a>
          <button class="btn btn-primary" type="submit">Salvar alterações</button>
        </div>
      </form>
    </div>
  </div>
</body>
</html>
"""


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_conn()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventario_id INTEGER NOT NULL,
                codigo_barras TEXT NOT NULL,
                nome_produto TEXT NOT NULL,
                quantidade REAL NOT NULL,
                origem TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (inventario_id) REFERENCES inventarios (id)
            );
            """
        )
        conn.commit()


def agora_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def fmt_num(valor: float) -> str:
    if float(valor).is_integer():
        return str(int(valor))
    return f"{valor:.3f}".rstrip("0").rstrip(".")


def inventario_ativo() -> sqlite3.Row:
    with closing(get_conn()) as conn:
        inventario_id = session.get("inventario_id")
        inventario = None
        if inventario_id:
            inventario = conn.execute(
                "SELECT * FROM inventarios WHERE id = ?", (inventario_id,)
            ).fetchone()

        if inventario is None:
            inventario = conn.execute(
                "SELECT * FROM inventarios ORDER BY id DESC LIMIT 1"
            ).fetchone()

        if inventario is None:
            nome = f"Levantamento {datetime.now().strftime('%d-%m-%Y %H-%M')}"
            conn.execute(
                "INSERT INTO inventarios (nome, criado_em) VALUES (?, ?)",
                (nome, agora_str()),
            )
            conn.commit()
            inventario = conn.execute(
                "SELECT * FROM inventarios ORDER BY id DESC LIMIT 1"
            ).fetchone()

        session["inventario_id"] = inventario["id"]
        return inventario


def listar_inventarios() -> list[sqlite3.Row]:
    with closing(get_conn()) as conn:
        return conn.execute(
            "SELECT * FROM inventarios ORDER BY id DESC"
        ).fetchall()


def dados_relatorio(inventario_id: int) -> dict[str, Any]:
    with closing(get_conn()) as conn:
        agrupados_db = conn.execute(
            """
            SELECT codigo_barras, nome_produto, origem, SUM(quantidade) AS quantidade_total
            FROM registros
            WHERE inventario_id = ?
            GROUP BY codigo_barras, nome_produto, origem
            ORDER BY nome_produto COLLATE NOCASE ASC, codigo_barras ASC
            """,
            (inventario_id,),
        ).fetchall()

        recentes_db = conn.execute(
            """
            SELECT *
            FROM registros
            WHERE inventario_id = ?
            ORDER BY id DESC
            """,
            (inventario_id,),
        ).fetchall()

        resumo_db = conn.execute(
            """
            SELECT
                COUNT(*) AS total_lancamentos,
                COALESCE(SUM(quantidade), 0) AS total_quantidade,
                COALESCE(SUM(CASE WHEN origem = 'ESTOQUE' THEN quantidade ELSE 0 END), 0) AS total_estoque,
                COALESCE(SUM(CASE WHEN origem = 'LOJA 5' THEN quantidade ELSE 0 END), 0) AS total_loja5
            FROM registros
            WHERE inventario_id = ?
            """,
            (inventario_id,),
        ).fetchone()

    agrupados = [
        {
            "codigo_barras": row["codigo_barras"],
            "nome_produto": row["nome_produto"],
            "origem": row["origem"],
            "quantidade_total": fmt_num(row["quantidade_total"]),
        }
        for row in agrupados_db
    ]
    recentes = [
        {
            "id": row["id"],
            "codigo_barras": row["codigo_barras"],
            "nome_produto": row["nome_produto"],
            "origem": row["origem"],
            "quantidade": fmt_num(row["quantidade"]),
            "criado_em": row["criado_em"],
        }
        for row in recentes_db
    ]
    resumo = {
        "total_linhas": len(agrupados),
        "total_quantidade": fmt_num(resumo_db["total_quantidade"]),
        "total_estoque": fmt_num(resumo_db["total_estoque"]),
        "total_loja5": fmt_num(resumo_db["total_loja5"]),
    }
    return {"agrupados": agrupados, "recentes": recentes, "resumo": resumo}


@app.before_request
def _init() -> None:
    init_db()


@app.route("/")
def index() -> str:
    inventario = inventario_ativo()
    relatorio = dados_relatorio(inventario["id"])
    return render_template_string(
        HTML,
        inventario=inventario,
        inventarios=listar_inventarios(),
        mensagem=request.args.get("mensagem", ""),
        erro=request.args.get("erro") == "1",
        **relatorio,
    )


@app.post("/inventario/novo")
def novo_inventario() -> Response:
    nome = request.form.get("nome_inventario", "").strip()
    if not nome:
        return redirect(url_for("index", mensagem="Informe um nome para o inventário.", erro=1))

    with closing(get_conn()) as conn:
        cursor = conn.execute(
            "INSERT INTO inventarios (nome, criado_em) VALUES (?, ?)",
            (nome, agora_str()),
        )
        conn.commit()
        session["inventario_id"] = cursor.lastrowid
    return redirect(url_for("index", mensagem="Novo inventário criado com sucesso."))


@app.post("/inventario/selecionar")
def selecionar_inventario() -> Response:
    inventario_id = request.form.get("inventario_id", "").strip()
    if not inventario_id.isdigit():
        return redirect(url_for("index", mensagem="Inventário inválido.", erro=1))
    session["inventario_id"] = int(inventario_id)
    return redirect(url_for("index", mensagem="Inventário alterado."))


@app.post("/adicionar")
def adicionar_item() -> Response:
    inventario = inventario_ativo()
    codigo_barras = request.form.get("codigo_barras", "").strip()
    nome_produto = request.form.get("nome_produto", "").strip()
    quantidade_raw = request.form.get("quantidade", "").strip().replace(",", ".")
    origem = request.form.get("origem", "").strip().upper()

    if not codigo_barras or not nome_produto or not quantidade_raw or origem not in {"ESTOQUE", "LOJA 5"}:
        return redirect(url_for("index", mensagem="Preencha todos os campos corretamente.", erro=1))

    try:
        quantidade = float(quantidade_raw)
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        return redirect(url_for("index", mensagem="Quantidade inválida.", erro=1))

    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO registros (inventario_id, codigo_barras, nome_produto, quantidade, origem, criado_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (inventario["id"], codigo_barras, nome_produto, quantidade, origem, agora_str()),
        )
        conn.commit()

    return redirect(url_for("index", mensagem="Item salvo com sucesso."))


@app.post("/inventario/limpar")
def limpar_inventario_atual() -> Response:
    inventario = inventario_ativo()
    with closing(get_conn()) as conn:
        conn.execute("DELETE FROM registros WHERE inventario_id = ?", (inventario["id"],))
        conn.commit()
    return redirect(url_for("index", mensagem="Todos os registros deste inventário foram apagados."))


@app.get("/buscar_produto")
def buscar_produto() -> Response:
    codigo = request.args.get("codigo", "").strip()
    if not codigo:
        return jsonify({"nome_produto": ""})

    with closing(get_conn()) as conn:
        row = conn.execute(
            """
            SELECT nome_produto
            FROM registros
            WHERE codigo_barras = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (codigo,),
        ).fetchone()

    return jsonify({"nome_produto": row["nome_produto"] if row else ""})


@app.route("/registro/<int:registro_id>/editar", methods=["GET", "POST"])
def editar_item(registro_id: int) -> Response | str:
    inventario = inventario_ativo()
    with closing(get_conn()) as conn:
        registro = conn.execute(
            "SELECT * FROM registros WHERE id = ? AND inventario_id = ?",
            (registro_id, inventario["id"]),
        ).fetchone()

        if registro is None:
            return redirect(url_for("index", mensagem="Registro não encontrado neste inventário.", erro=1))

        if request.method == "POST":
            codigo_barras = request.form.get("codigo_barras", "").strip()
            nome_produto = request.form.get("nome_produto", "").strip()
            quantidade_raw = request.form.get("quantidade", "").strip().replace(",", ".")
            origem = request.form.get("origem", "").strip().upper()

            if not codigo_barras or not nome_produto or not quantidade_raw or origem not in {"ESTOQUE", "LOJA 5"}:
                return redirect(url_for("index", mensagem="Preencha todos os campos corretamente para editar o item.", erro=1))

            try:
                quantidade = float(quantidade_raw)
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                return redirect(url_for("index", mensagem="Quantidade inválida na edição do item.", erro=1))

            conn.execute(
                """
                UPDATE registros
                SET codigo_barras = ?, nome_produto = ?, quantidade = ?, origem = ?
                WHERE id = ? AND inventario_id = ?
                """,
                (codigo_barras, nome_produto, quantidade, origem, registro_id, inventario["id"]),
            )
            conn.commit()
            return redirect(url_for("index", mensagem="Item atualizado com sucesso."))

    return render_template_string(HTML_EDIT, registro=registro)


@app.post("/registro/<int:registro_id>/excluir")
def excluir_item(registro_id: int) -> Response:
    inventario = inventario_ativo()
    with closing(get_conn()) as conn:
        cursor = conn.execute(
            "DELETE FROM registros WHERE id = ? AND inventario_id = ?",
            (registro_id, inventario["id"]),
        )
        conn.commit()

    if cursor.rowcount == 0:
        return redirect(url_for("index", mensagem="Registro não encontrado para exclusão.", erro=1))

    return redirect(url_for("index", mensagem="Item excluído com sucesso."))


@app.get("/exportar/csv")
def exportar_csv() -> Response:
    inventario = inventario_ativo()
    relatorio = dados_relatorio(inventario["id"])

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Inventário", inventario["nome"]])
    writer.writerow(["Emitido em", agora_str()])
    writer.writerow([])
    writer.writerow(["Código", "Produto", "Origem", "Quantidade"])

    for row in relatorio["agrupados"]:
        writer.writerow([
            row["codigo_barras"],
            row["nome_produto"],
            row["origem"],
            row["quantidade_total"],
        ])

    csv_data = output.getvalue().encode("utf-8-sig")
    nome_arquivo = f"relatorio_{inventario['nome'].replace(' ', '_')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )


@app.get("/health")
def health() -> Response:
    return jsonify({"status": "ok"})


@app.get("/relatorio")
def relatorio_impressao() -> str:
    inventario = inventario_ativo()
    relatorio = dados_relatorio(inventario["id"])
    return render_template_string(
        HTML_PRINT,
        inventario=inventario,
        emitido_em=agora_str(),
        **relatorio,
    )


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
