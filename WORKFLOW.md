# Workflow Completo de Desarrollo

Este documento explica el workflow completo de desarrollo para el SDK de Datadis, incluyendo estrategias de branching, comandos Git, mejores prácticas y el sistema de publicación automática.

## Tabla de Contenidos

1. [Estrategia de Branching](#estrategia-de-branching)
2. [Flujo de Desarrollo Completo](#flujo-de-desarrollo-completo)
3. [Comandos Git Esenciales](#comandos-git-esenciales)
4. [Buenas Prácticas](#buenas-prácticas)
5. [Sistema de Publicación Automática](#sistema-de-publicación-automática)
6. [Resolución de Conflictos](#resolución-de-conflictos)
7. [Comandos de Emergencia](#comandos-de-emergencia)

---

# Estrategia de Branching

## Estructura de Ramas

### Ramas Permanentes

#### `main`
- **Propósito**: Código production-ready únicamente
- **Características**:
  - Solo recibe merges desde `develop`
  - Cada push se auto-publica a PyPI (si cambió versión)
  - Siempre debe estar funcional
  - Nunca trabajar directamente aquí

#### `develop`
- **Propósito**: Integración y testing de features
- **Características**:
  - Recibe todas las ramas fugaces (feature/fix/docs)
  - Buffer de testing antes de main
  - Donde se detectan conflictos de integración
  - Donde se prueban todas las features juntas

### Ramas Fugaces (Temporales)

#### `feature/*` - Nuevas funcionalidades
```bash
feature/add-consumption-endpoint
feature/improve-authentication-flow
feature/23-add-user-dashboard  # Con número de issue
```

#### `fix/*` - Corrección de bugs
```bash
fix/authentication-timeout
fix/memory-leak-client
fix/15-broken-api-response  # Con número de issue
```

#### `docs/*` - Cambios de documentación
```bash
docs/update-readme-pypi
docs/add-api-examples
docs/fix-sphinx-errors
```

## Reglas de Branching

### Prohibido
- Merge directo desde ramas fugaces a `main`
- Push directo a `main` o `develop`
- Mantener ramas fugaces después del merge

### Obligatorio
- Todas las ramas fugaces van a `develop` primero
- Solo `develop` puede ir a `main`
- Borrar ramas fugaces después del merge
- Probar localmente antes de push

---

# Flujo de Desarrollo Completo

## 1. Inicio de Nueva Feature/Fix/Docs

### Configuración Inicial (Solo una vez)
```bash
# Clonar y configurar repositorio
git clone https://github.com/TacoronteRiveroCristian/ctr-datadis.git
cd ctr-datadis

# Crear rama develop si no existe
git checkout -b develop
git push -u origin develop
```

### Para Cada Nueva Tarea
```bash
# 1. Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# 2. Crear rama fugaz según el tipo
git checkout -b feature/add-new-endpoint    # Para nuevas funcionalidades
git checkout -b fix/authentication-bug     # Para bugs
git checkout -b docs/update-readme         # Para documentación
git checkout -b feature/23-user-dashboard  # Con número de issue
```

## 2. Desarrollo Local

### Hacer Cambios
```bash
# Editar archivos necesarios
# Añadir/modificar código
# Añadir/modificar tests (OBLIGATORIO)
```

### Verificación Local (SIEMPRE antes de commit)
```bash
# Formatear código
poetry run black datadis_python/
poetry run isort datadis_python/

# Verificar calidad
poetry run flake8 datadis_python/
poetry run mypy datadis_python/

# Ejecutar tests
poetry run pytest

# O usar script completo (si existe)
./scripts/quality_check.sh fix
```

### Commit
```bash
# Añadir archivos
git add .

# Commit con mensaje descriptivo
git commit -m "feat: add new consumption endpoint with pagination"
git commit -m "fix: resolve authentication timeout issue"
git commit -m "docs: update PyPI README with correct links"

# Push a la rama fugaz
git push origin feature/add-new-endpoint
```

## 3. Integración a Develop

### Actualizar Base (Si han pasado días)
```bash
# En tu rama fugaz
git fetch origin
git rebase origin/develop

# Resolver conflictos si los hay
# Volver a probar que todo funciona
poetry run pytest
```

### Merge a Develop
```bash
# Cambiar a develop
git checkout develop
git pull origin develop

# Mergear tu rama fugaz
git merge feature/add-new-endpoint

# Push a develop
git push origin develop
```

### Limpiar Rama Fugaz
```bash
# Borrar rama local
git branch -d feature/add-new-endpoint

# Borrar rama remota
git push origin --delete feature/add-new-endpoint
```

## 4. Testing en Develop

### Verificación Completa
```bash
# En develop, ejecutar todos los tests
git checkout develop
poetry run pytest --cov=datadis_python

# Verificar calidad
poetry run black datadis_python/
poetry run isort datadis_python/
poetry run flake8 datadis_python/
poetry run mypy datadis_python/

# Probar instalación
poetry build
```

### Si Todo Funciona → Continuar
### Si Hay Problemas → Crear Fix

```bash
# Si hay problemas
git checkout -b fix/develop-integration-issue
# Corregir problemas
# Repetir proceso de merge a develop
```

## 5. Release a Main

### Preparar Release (Solo cuando develop esté estable)
```bash
# En develop, actualizar versión para publicar
# Editar pyproject.toml
version = "0.2.4"  # Incrementar versión

# Commit del cambio de versión
git add pyproject.toml
git commit -m "bump: version 0.2.4"
git push origin develop
```

### Merge a Main
```bash
# Cambiar a main
git checkout main
git pull origin main

# Mergear develop
git merge develop

# Push a main (Trigger automático de publicación)
git push origin main
```

### Resultado Automático
- GitHub Actions ejecuta tests
- Publica a TestPyPI y PyPI
- Crea GitHub Release
- Actualiza ReadTheDocs

---

# Comandos Git Esenciales

## Comandos Diarios

### Estado y Navegación
```bash
git status                          # Ver estado actual
git branch                          # Ver ramas locales
git branch -a                       # Ver todas las ramas (locales + remotas)
git log --oneline                   # Ver historial resumido
git log --graph --oneline --all     # Ver historial visual de todas las ramas
```

### Cambio de Ramas
```bash
git checkout develop                # Cambiar a develop
git checkout -b feature/new-thing   # Crear y cambiar a nueva rama
git checkout -                      # Cambiar a rama anterior
```

### Sincronización
```bash
git fetch origin                    # Descargar cambios remotos sin aplicar
git pull origin develop             # Descargar y aplicar cambios de develop
git push origin feature/my-branch   # Subir rama al remoto
git push -u origin feature/my-branch # Primera vez (set upstream)
```

## Comandos de Rebase

### Rebase Básico
```bash
# En tu rama fugaz
git fetch origin
git rebase origin/develop           # Actualizar base a develop más reciente
```

### Resolución de Conflictos en Rebase
```bash
# Si hay conflictos durante rebase
git status                          # Ver archivos en conflicto
# Editar archivos para resolver conflictos
git add archivo-resuelto.py
git rebase --continue              # Continuar rebase

# Si quieres cancelar rebase
git rebase --abort
```

## Comandos de Merge

### Merge Normal
```bash
git checkout develop
git merge feature/my-branch         # Merge sin fast-forward
git merge --no-ff feature/my-branch # Forzar commit de merge
```

### Merge con Squash (Opcional)
```bash
git merge --squash feature/my-branch # Combinar commits en uno solo
git commit -m "feat: complete feature implementation"
```

## Comandos de Limpieza

### Borrar Ramas
```bash
git branch -d feature/completed     # Borrar rama local (safe)
git branch -D feature/force-delete  # Forzar borrado local
git push origin --delete feature/old # Borrar rama remota
```

### Limpiar Referencias
```bash
git remote prune origin             # Limpiar referencias remotas obsoletas
git gc                              # Garbage collection local
```

---

# Buenas Prácticas

## Commits

### Mensajes de Commit (Conventional Commits)
```bash
feat: add new consumption data endpoint
fix: resolve authentication timeout in client
docs: update API documentation with examples
test: add unit tests for authentication flow
refactor: improve error handling in base client
chore: update dependencies to latest versions
```

### Tamaño de Commits
- **Un cambio lógico por commit**
- **Commits pequeños y frecuentes**
- **Cada commit debe compilar y pasar tests**

### Que NO hacer en Commits
```bash
# Malo - muy general
git commit -m "fix stuff"
git commit -m "work in progress"
git commit -m "changes"

# Malo - múltiples cambios no relacionados
git add .  # Incluye changes de API + docs + tests de otra feature
git commit -m "various improvements"
```

## Branching

### Nomenclatura Consistente
```bash
# Bueno
feature/add-consumption-endpoint
fix/authentication-timeout
docs/update-api-examples
hotfix/critical-security-patch

# Con issue numbers
feature/23-user-dashboard
fix/45-memory-leak
docs/67-api-documentation

# Malo
my-branch
cristian-changes
test-branch
fix
```

### Ciclo de Vida de Ramas
1. **Crear desde develop actualizado**
2. **Desarrollar con commits frecuentes**
3. **Probar localmente**
4. **Rebase si es necesario**
5. **Merge a develop**
6. **Borrar inmediatamente**

## Colaboración

### Comunicación
- **Crear issues para bugs/features**
- **Usar números de issue en nombres de rama**
- **Comentar en issues el progreso**
- **Avisar antes de cambios grandes**

### Revisión
```bash
# Revisar cambios antes de commit
git diff                            # Ver cambios no staged
git diff --staged                   # Ver cambios staged
git diff develop                    # Ver diferencias con develop
```

### Testing
- **Escribir tests para cada feature**
- **Ejecutar tests antes de cada push**
- **Mantener coverage alto**
- **Tests deben ser independientes**

## Seguridad

### Secretos y Credenciales
- **NUNCA commitear tokens/passwords**
- **Usar variables de entorno**
- **Verificar con git diff antes de add**
- **Usar .gitignore para archivos sensibles**

### Verificación Antes de Push
```bash
# Checklist antes de push
git status                          # ¿Hay archivos no deseados?
git diff --staged                   # ¿Los cambios son correctos?
poetry run pytest                  # ¿Pasan todos los tests?
poetry run mypy datadis_python/    # ¿Sin errores de tipos?
```

---

# Resolución de Conflictos

## Tipos de Conflictos

### 1. Conflictos de Merge
Ocurren cuando dos ramas modifican las mismas líneas de código.

```bash
# Al hacer merge
git checkout develop
git merge feature/my-branch
# ERROR: Merge conflict in archivo.py
```

### 2. Conflictos de Rebase
Ocurren cuando rebases tu rama sobre cambios que afectan tu código.

```bash
# Al hacer rebase
git rebase origin/develop
# ERROR: Rebase conflict in archivo.py
```

## Resolución Paso a Paso

### Identificar Conflictos
```bash
git status
# Muestra archivos en conflicto
# Unmerged paths:
#   both modified: datadis_python/client/base.py
```

### Resolver Conflictos Manualmente
```python
# Archivo con conflicto
<<<<<<< HEAD
def authenticate(self, username, password):
    # Tu versión
    return self._login_with_retry(username, password)
=======
def authenticate(self, username, password):
    # Versión de develop
    return self._secure_login(username, password)
>>>>>>> develop
```

**Resolver editando:**
```python
def authenticate(self, username, password):
    # Versión combinada (la mejor de ambas)
    return self._secure_login_with_retry(username, password)
```

### Completar Resolución
```bash
# Añadir archivo resuelto
git add datadis_python/client/base.py

# Para merge
git commit -m "resolve: merge conflicts in authentication"

# Para rebase
git rebase --continue
```

## Estrategias de Prevención

### 1. Ramas de Vida Corta
```bash
# Malo - rama longeva
feature/big-refactor  # 2 semanas de trabajo

# Bueno - ramas cortas
feature/auth-endpoint     # 2-3 días
feature/auth-validation   # 1-2 días
feature/auth-tests        # 1 día
```

### 2. Rebase Frecuente
```bash
# Cada 2-3 días en ramas largas
git fetch origin
git rebase origin/develop
```

### 3. Comunicación de Equipo
- Avisar cuando trabajas en archivos core
- Coordinar refactorings grandes
- Mergear features pequeñas frecuentemente

## Comandos de Emergencia

### Deshacer Últimos Commits (Local)
```bash
# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Deshacer último commit (perder cambios)
git reset --hard HEAD~1

# Deshacer múltiples commits
git reset --soft HEAD~3  # Últimos 3 commits
```

### Deshacer Cambios en Archivos
```bash
# Descartar cambios no staged
git checkout -- archivo.py
git restore archivo.py

# Descartar cambios staged
git reset HEAD archivo.py
git restore --staged archivo.py

# Descartar todos los cambios
git reset --hard HEAD
```

### Recuperar Trabajo Perdido
```bash
# Ver historial de todos los cambios
git reflog

# Recuperar commit "perdido"
git cherry-pick abc1234

# Crear rama desde commit perdido
git checkout -b recovery abc1234
```

### Emergencias en Ramas

#### Cambiar a Rama Equivocada
```bash
# Si commiteaste en main por error
git checkout main
git reset --soft HEAD~1  # Deshacer commit
git stash                # Guardar cambios
git checkout develop     # Ir a rama correcta
git stash pop           # Aplicar cambios
```

#### Rama Corrupta
```bash
# Crear nueva rama desde main
git checkout main
git checkout -b feature/recovery

# Cherry-pick commits específicos
git cherry-pick abc123
git cherry-pick def456
```

### Emergencias en Remoto

#### Push Forzado (PELIGROSO)
```bash
# Solo en ramas fugaces, NUNCA en main/develop
git push --force-with-lease origin feature/my-branch

# Más seguro que --force
# Falla si alguien más hizo push
```

#### Revertir Commits Públicos
```bash
# Crear commit que revierte cambios
git revert HEAD           # Revertir último commit
git revert HEAD~2..HEAD   # Revertir últimos 2 commits

# Push el revert
git push origin main
```

### Herramientas de Ayuda

#### Merge Tools
```bash
# Configurar merge tool (VSCode)
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Usar merge tool
git mergetool
```

#### Aliases Útiles
```bash
# Configurar aliases
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Usar aliases
git unstage archivo.py
git last
```

## Checklist de Emergencia

### Antes de Cualquier Comando Destructivo
1. **¿Está commiteado mi trabajo?**
2. **¿Está pusheado a remoto?**
3. **¿Alguien más puede estar afectado?**
4. **¿Tengo backup?**

### Si Todo Sale Mal
```bash
# 1. No entrar en pánico
# 2. NO hacer más comandos destructivos
# 3. Hacer backup inmediato
git stash
git branch backup-$(date +%Y%m%d-%H%M%S)

# 4. Buscar ayuda o revisar reflog
git reflog --all

# 5. En último caso, re-clonar repo
```

---

# Sistema de Publicación Automática

## Resumen del Workflow Automático

### Un Solo Comando: Push a Main
Todo se publica automáticamente con un simple:
```bash
git push origin main
```

### Qué se Publica Automáticamente

| Servicio | Trigger | Condición |
|----------|---------|-----------|
| **ReadTheDocs** | Push a `main` | Siempre |
| **PyPI** | Push a `main` | Solo si cambió la versión |
| **GitHub Release** | Push a `main` | Solo si cambió la versión |

## Proceso Completo

### 1. Desarrollo Local
```bash
# Hacer cambios en el código
# ...

# Ejecutar quality checks
./scripts/quality_check.sh fix

# Actualizar versión en pyproject.toml (para publicar)
# version = "0.1.4"  # Cambiar aquí

# Commit y push
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main
```

### 2. Automatización en GitHub

#### Detección de Cambios
- GitHub Actions verifica si cambió la versión en `pyproject.toml`
- Si NO cambió: Solo actualiza ReadTheDocs
- Si SÍ cambió: Ejecuta pipeline completo

#### Tests y Quality Checks
- Ejecuta tests en Python 3.8, 3.9, 3.10, 3.11, 3.12
- Verifica formateo (Black, isort)
- Ejecuta linting (flake8)
- Verifica tipos (mypy)
- Genera coverage report

#### Publicación (Solo si cambió versión)
1. **TestPyPI**: Publica primero en ambiente de prueba
2. **PyPI**: Publica en producción
3. **GitHub Release**: Crea release automático con tag

#### Documentación
- ReadTheDocs se actualiza automáticamente
- Sphinx regenera toda la documentación
- Incluye API docs, ejemplos y guías

## Configuración Requerida

### 1. Secretos de GitHub
Añadir en `Settings > Secrets and variables > Actions`:

```bash
PYPI_API_TOKEN=pypi-...          # Token de PyPI
TESTPYPI_API_TOKEN=pypi-...      # Token de TestPyPI (opcional)
```

### 2. ReadTheDocs
1. Conectar repositorio en [readthedocs.org](https://readthedocs.org)
2. El archivo `.readthedocs.yml` ya está configurado
3. Builds automáticos activados

### 3. PyPI Tokens
```bash
# Generar tokens en:
# PyPI: https://pypi.org/manage/account/token/
# TestPyPI: https://test.pypi.org/manage/account/token/
```

## Workflow para Diferentes Escenarios

### Bug Fix (Sin publicar)
```bash
# Solo corregir código, NO cambiar versión
git add .
git commit -m "fix: corregir bug en autenticación"
git push origin main
# Solo se actualiza ReadTheDocs
```

### Nueva Versión
```bash
# 1. Cambiar versión en pyproject.toml
version = "0.1.5"

# 2. Commit y push
git add .
git commit -m "feat: nueva funcionalidad de datos reactivos"
git push origin main

# Se ejecuta:
# - Tests en todas las versiones de Python
# - Publicación en TestPyPI y PyPI
# - Creación de GitHub Release
# - Actualización de ReadTheDocs
```

### Solo Documentación
```bash
# Cambios solo en docs/ o README.md
git add .
git commit -m "docs: actualizar ejemplos"
git push origin main
# Solo se actualiza ReadTheDocs
```

## Scripts Locales Disponibles

### Desarrollo Diario
```bash
./scripts/quality_check.sh fix    # Corregir formato y ejecutar tests
./scripts/generate_docs.sh clean  # Generar documentación localmente
```

### Publicación Manual (Emergencias)
```bash
./scripts/complete_workflow.sh test  # Publicar en TestPyPI
./scripts/complete_workflow.sh prod  # Publicar en PyPI producción
```

## Monitoreo

### GitHub Actions
- Ver progreso en `Actions` tab del repositorio
- Logs detallados de cada paso
- Notificaciones por email si falla

### ReadTheDocs
- Panel en [readthedocs.org](https://readthedocs.org)
- Builds automáticos en cada push
- Logs de Sphinx disponibles

### PyPI
- Paquetes aparecen automáticamente
- Verificar en https://pypi.org/project/ctr-datadis/

## Solución de Problemas

### Falla la Publicación en PyPI
```bash
# Verificar secretos en GitHub
# Verificar que la versión sea única
# Revisar logs en GitHub Actions
```

### Falla ReadTheDocs
```bash
# Verificar .readthedocs.yml
# Revisar requirements.txt en docs/
# Verificar conf.py de Sphinx
```

### Tests Fallan
```bash
# Ejecutar localmente primero
./scripts/quality_check.sh

# Corregir errores antes de push
```

## Ventajas de este Workflow

1. **Automatización Completa**: Un solo push publica todo
2. **Seguridad**: Tests obligatorios antes de publicar
3. **Documentación Sincronizada**: Siempre actualizada
4. **Releases Automáticos**: Con tags y changelogs
5. **Testing Múltiple**: En todas las versiones de Python
6. **Rápido**: Solo publica si realmente hay cambios

## Recursos Adicionales

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [ReadTheDocs Configuration](https://docs.readthedocs.io/en/stable/config-file/v2.html)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Poetry Documentation](https://python-poetry.org/docs/)

---

# Ejemplos Prácticos Completos

## Ejemplo 1: Arreglar Bug en README PyPI

### Problema: Links incorrectos en PyPI
```bash
# 1. Crear issue (opcional)
# En GitHub: "Fix incorrect links in PyPI README" → Issue #45

# 2. Configuración inicial
git checkout develop
git pull origin develop

# 3. Crear rama fugaz
git checkout -b docs/45-fix-pypi-readme-links

# 4. Hacer cambios
# Editar README.md con links correctos

# 5. Verificar localmente
git diff                        # Ver cambios
poetry run pytest              # Asegurar que no rompiste nada

# 6. Commit
git add README.md
git commit -m "docs: fix incorrect PyPI documentation links

Fixes #45"

# 7. Push rama fugaz
git push origin docs/45-fix-pypi-readme-links

# 8. Merge a develop
git checkout develop
git pull origin develop        # Por si hubo cambios
git merge docs/45-fix-pypi-readme-links

# 9. Push develop
git push origin develop

# 10. Limpiar
git branch -d docs/45-fix-pypi-readme-links
git push origin --delete docs/45-fix-pypi-readme-links

# 11. Si necesitas publicar inmediatamente
# Editar pyproject.toml: version = "0.2.4"
git add pyproject.toml
git commit -m "bump: version 0.2.4 - fix PyPI documentation"
git push origin develop

# 12. Release a main
git checkout main
git pull origin main
git merge develop
git push origin main           # Auto-publica a PyPI
```

## Ejemplo 2: Nueva Feature con Tests

### Problema: Agregar endpoint de consumo por rangos
```bash
# 1. Crear issue
# "Add consumption data range endpoint" → Issue #47

# 2. Configuración
git checkout develop
git pull origin develop

# 3. Crear rama
git checkout -b feature/47-consumption-range-endpoint

# 4. Desarrollo iterativo
# Primer commit: Agregar modelo
# Editar datadis_python/models/consumption.py
git add datadis_python/models/consumption.py
git commit -m "feat: add ConsumptionRangeData model for date ranges"
git push origin feature/47-consumption-range-endpoint

# Segundo commit: Agregar método al cliente
# Editar datadis_python/client/v1/simple_client.py
git add datadis_python/client/v1/simple_client.py
git commit -m "feat: add get_consumption_range method to SimpleDatadisClientV1"
git push origin feature/47-consumption-range-endpoint

# Tercer commit: Agregar tests
# Crear tests/test_consumption_range.py
git add tests/test_consumption_range.py
git commit -m "test: add comprehensive tests for consumption range feature"
git push origin feature/47-consumption-range-endpoint

# 5. Verificación completa antes de merge
poetry run black datadis_python/
poetry run isort datadis_python/
poetry run flake8 datadis_python/
poetry run mypy datadis_python/
poetry run pytest --cov=datadis_python

# 6. Actualizar base (si han pasado días)
git fetch origin
git rebase origin/develop
# Resolver conflictos si los hay
poetry run pytest              # Volver a probar después del rebase

# 7. Merge a develop
git checkout develop
git pull origin develop
git merge feature/47-consumption-range-endpoint
git push origin develop

# 8. Verificar en develop
poetry run pytest --cov=datadis_python
poetry build                   # Probar build

# 9. Limpiar
git branch -d feature/47-consumption-range-endpoint
git push origin --delete feature/47-consumption-range-endpoint

# 10. Actualizar documentación si necesario
git checkout -b docs/update-consumption-range-docs
# Actualizar docs/
git add docs/
git commit -m "docs: add documentation for consumption range endpoint"
# Repetir proceso de merge

# 11. Release cuando develop esté estable
# Incrementar versión en pyproject.toml
version = "0.3.0"  # Major feature
git add pyproject.toml
git commit -m "bump: version 0.3.0 - add consumption range functionality"
git push origin develop

# 12. Deploy a main
git checkout main
git pull origin main
git merge develop
git push origin main           # Auto-publica nueva versión
```

## Ejemplo 3: Hotfix Crítico en Producción

### Problema: Bug crítico en autenticación que afecta usuarios
```bash
# 1. Crear issue urgente
# "CRITICAL: Authentication timeout causing user lockouts" → Issue #50

# 2. Trabajar desde main (excepción)
git checkout main
git pull origin main

# 3. Crear hotfix
git checkout -b hotfix/50-auth-timeout-critical

# 4. Fix rápido y focused
# Editar datadis_python/client/base.py
git add datadis_python/client/base.py
git commit -m "hotfix: increase authentication timeout to prevent lockouts

Critical fix for production issue #50"

# 5. Tests mínimos pero esenciales
poetry run pytest tests/test_authentication.py
git add tests/test_authentication.py
git commit -m "test: add timeout test for authentication hotfix"

# 6. Push hotfix
git push origin hotfix/50-auth-timeout-critical

# 7. Merge directo a main (excepción)
git checkout main
git merge hotfix/50-auth-timeout-critical

# 8. Incrementar versión patch
# pyproject.toml: version = "0.2.4" → "0.2.5"
git add pyproject.toml
git commit -m "bump: version 0.2.5 - critical authentication hotfix"

# 9. Deploy inmediato
git push origin main           # Auto-publica hotfix

# 10. Backport a develop
git checkout develop
git pull origin develop
git merge main                 # Traer hotfix a develop
git push origin develop

# 11. Limpiar
git branch -d hotfix/50-auth-timeout-critical
git push origin --delete hotfix/50-auth-timeout-critical

# 12. Comunicar
# Actualizar issue #50 con "Fixed in v0.2.5"
# Notificar a usuarios del fix
```

## Comandos de Referencia Rápida

### Workflow Diario
```bash
# Iniciar trabajo
git checkout develop && git pull origin develop
git checkout -b feature/nueva-funcionalidad

# Durante desarrollo
poetry run pytest && git add . && git commit -m "feat: nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# Finalizar trabajo
git checkout develop && git pull origin develop
git merge feature/nueva-funcionalidad && git push origin develop
git branch -d feature/nueva-funcionalidad
git push origin --delete feature/nueva-funcionalidad
```

### Release
```bash
# Preparar release
git checkout develop
# Editar pyproject.toml: incrementar versión
git add pyproject.toml && git commit -m "bump: version X.Y.Z"
git push origin develop

# Deploy
git checkout main && git pull origin main
git merge develop && git push origin main
```

### Emergencia
```bash
# Backup inmediato
git stash && git branch backup-$(date +%Y%m%d-%H%M%S)

# Ver qué pasó
git reflog --all

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1
```

---

**Tip Final**: Siempre incrementa la versión en `pyproject.toml` cuando quieras publicar una nueva versión. El sistema detecta automáticamente los cambios de versión y activa la publicación completa.

**Recuerda**: Este documento es tu guía completa. Cuando tengas dudas en 2 meses, vuelve aquí y encuentra exactamente lo que necesitas hacer.
