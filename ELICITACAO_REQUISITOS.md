# 📄 ELICITAÇÃO DE REQUISITOS — PROTOTIPAÇÃO EVOLUTIVA

## 🎯 Objetivo

Descrever o processo de elicitação de requisitos para um sistema de cadastro e acompanhamento de ONGs, utilizando a técnica de **prototipagem evolutiva**, com apoio de brainstorming.

---

## 🧠 Técnica Utilizada

A técnica adotada foi **prototipagem evolutiva**, seguindo as etapas:

1. Brainstorm inicial entre os desenvolvedores
2. Estruturação de entidades
3. Criação de Fluxo de Telas
4. Definição de requisitos (épicos e histórias)
5. Refinamento iterativo

---

## 🪄 Etapas Realizadas

### 1. Brainstorm

Foram levantadas ideias iniciais para o sistema, incluindo:

- Tipos de usuários:
  - Explorador (usuário comum)
  - Organizador (ONG)
- Funcionalidades principais:
  - Visualização de ONGs e campanhas
  - Interesse em voluntariado
- Estrutura inicial do sistema

📌 **Observação:**  
O voluntariado foi modelado como **manifestação de interesse**, e não como gestão completa, simplificando o sistema.


---
## 🔗 Evidências

### 🧩 Modelagem (UML)

Modelo de entidades proposto:

```plaintext
+----------------------+
|       Usuario       |
+----------------------+
| id: UUID            |
| nome: string        |
| email: string       |
| senha: string       |
| tipo: enum          | -> (EXPLORADOR, ORGANIZADOR, ADMIN)
| created_at: date    |
+----------------------+

+----------------------+
|        ONG           |
+----------------------+
| id: UUID            |
| nome: string        |
| descricao: text     |
| categoria: string   |
| localizacao: string |
| status: enum        | -> (PENDENTE, APROVADA, REJEITADA)
| owner_id: UUID      |
+----------------------+

           |
           | (1:N)
           v

+----------------------+
|      Campanha        |
+----------------------+
| id: UUID            |
| titulo: string      |
| descricao: text     |
| meta_valor: decimal |
| valor_atual: decimal|
| data_inicio: date   |
| data_fim: date      |
| status: enum        | -> (ATIVA, ENCERRADA)
| ong_id: UUID        |
+----------------------+

     -------------------
     |                 |
     v                 v

+----------------------+        +----------------------+
|       Doacao         |        | InteresseVoluntario  |
+----------------------+        +----------------------+
| id: UUID            |        | id: UUID            |
| valor: decimal      |        | mensagem: text      |
| status: enum        |        | status: enum        |
| data: date          |        | (ENVIADO, VISUALIZADO)
| usuario_id: UUID    |        | usuario_id: UUID    |
| campanha_id: UUID   |        | campanha_id: UUID   |
+----------------------+        +----------------------+

```
---
### 🖼️ Navegação entre Telas

- **Landing Page**
  - TO DO: Diagrama de Telas e possível navegação

---

### 📋 Épicos e Histórias

| Épico | História | Descrição |
|------|--------|----------|
| Exploração e Engajamento | Visualizar ONGs e Campanhas ✅| Navegar e visualizar detalhes |
| | Buscar e Filtrar ✅| Encontrar ONGs/campanhas |
| | Demonstrar Interesse/Voluntario ❌| Usuário/Explorador mostrar interesse em campanhas ou em voluntariado|
| | Realizar Doação ❌| Usuário/Explorador poder contribuir financeiramente |
| Gestão de ONGs | Cadastro de ONG ✅| Criar ONG na plataforma |
| | Criar Campanha ⚠️| Hablitar Usuário de ONG criar campanhas |
| | Visualizar Engajamento ❌| Acompanhar doações/interesses |
| | Gerenciar Campanhas ⚠️| Editar e Encerrar campanhas |

Legenda:
- ✅: Feito
- ⚠️: Deve ser Feito
- ❌: Não Feito mas pode ser feito
---

## 📌 Observações Finais

- O sistema foi projetado como **MVP**
- O voluntariado foi simplificado para reduzir complexidade
- A prototipagem será refinada após feedback do professor