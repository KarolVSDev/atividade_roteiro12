# Atividade — Versionamento e Organização do Projeto com Git

## 1. Objetivo

Esta atividade tem como objetivo praticar o uso do **Git e GitHub** para controle de versão, organização do projeto e gerenciamento de diferentes linhas de desenvolvimento por meio de branches.

Durante a atividade, foram realizadas operações de criação, exclusão, atualização e sincronização de branches, além do acompanhamento do histórico de commits.

---

## 2. Tecnologias e ferramentas

* Git
* GitHub
* PowerShell
* Visual Studio Code

---

## 3. Estrutura de branches

O projeto utiliza branches para separar o desenvolvimento das diferentes funcionalidades.

Estrutura utilizada:

```text
main
│
└── develop
    │
    ├── feature/processo1
    ├── feature/processo2
    ├── feature/processo3
    ├── feature/processo4
    ├── feature/processo5
    └── feature/integracao
```

### Branches principais

#### `main`

Branch destinada à versão principal e estável do projeto.

#### `develop`

Branch utilizada para integração das funcionalidades desenvolvidas nas branches de feature.

#### `feature/*`

Branches destinadas ao desenvolvimento de funcionalidades específicas do projeto.

---

## 4. Comandos Git utilizados

### Verificar o status do projeto

```bash
git status
```

### Visualizar o histórico de commits

```bash
git log --oneline --decorate --graph --all
```

### Atualizar a branch local

```bash
git pull origin main
```

### Criar uma nova branch

```bash
git switch -c feature/nome-da-feature
```

### Enviar a branch para o GitHub

```bash
git push -u origin feature/nome-da-feature
```

### Trocar de branch

```bash
git switch nome-da-branch
```

### Listar branches locais

```bash
git branch
```

### Listar branches locais e remotas

```bash
git branch -a
```

### Excluir uma branch local

```bash
git branch -D feature/nome-da-feature
```

### Excluir uma branch remota

```bash
git push origin --delete feature/nome-da-feature
```

---

## 5. Organização do desenvolvimento

Cada funcionalidade deve ser desenvolvida em sua própria branch.

Exemplo:

```bash
git switch develop
git pull origin develop

git switch -c feature/processo1
```

Após a implementação da funcionalidade, os arquivos devem ser adicionados e commitados:

```bash
git add .
git commit -m "feat: descrição da alteração"
```

Em seguida, a branch deve ser enviada para o GitHub:

```bash
git push -u origin feature/processo1
```

Após a conclusão, a funcionalidade poderá ser integrada à branch `develop` por meio de um Pull Request.

---

## 6. Histórico e organização

Durante o desenvolvimento, foi identificado que algumas branches haviam sido criadas a partir de commits anteriores e, por isso, não continham arquivos adicionados posteriormente ao projeto.

Para solucionar o problema, as branches que não possuíam a estrutura necessária foram removidas e recriadas a partir de uma base atualizada.

Esse procedimento garante que as novas branches iniciem com a estrutura de arquivos correspondente ao estado atual do projeto.

---

## 7. Boas práticas

* Criar branches de funcionalidade a partir da branch de desenvolvimento atualizada.
* Utilizar nomes descritivos para as branches.
* Realizar commits pequenos e objetivos.
* Utilizar mensagens de commit claras.
* Atualizar a branch antes de iniciar uma nova funcionalidade.
* Evitar trabalhar diretamente na `main`.
* Enviar as branches para o GitHub regularmente.
* Utilizar Pull Requests para integrar funcionalidades.
* Verificar o histórico com `git log` quando houver dúvidas sobre a origem de uma branch.

---

## 8. Exemplo de fluxo de trabalho

```text
1. Atualizar a develop
        ↓
2. Criar uma feature
        ↓
3. Desenvolver a funcionalidade
        ↓
4. git add .
        ↓
5. git commit
        ↓
6. git push
        ↓
7. Criar Pull Request
        ↓
8. Integrar na develop
        ↓
9. Após validação, integrar na main
```

---

## 9. Conclusão

A atividade permitiu compreender na prática o funcionamento do **controle de versão com Git**, especialmente a criação e gerenciamento de branches.

Também foi possível compreender que uma branch é criada a partir de um determinado commit e **não recebe automaticamente alterações feitas posteriormente em outras branches**. Por esse motivo, é importante definir corretamente a branch de origem e mantê-la atualizada durante o desenvolvimento.

O uso adequado de branches facilita a organização do projeto, permite o desenvolvimento paralelo de funcionalidades e reduz conflitos durante a integração das alterações.
