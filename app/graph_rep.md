# Project Structure Visualization (Mermaid)

```mermaid
graph TD
    A[app.py] -->|uses| B[utils/fetch_rates.py]
    A -->|uses| C[utils/pdf_generator.py]
    A -->|uses| D[streamlit]
    A -->|uses| E[pandas]
    A -->|uses| F[matplotlib]
    
    B -->|uses| E
    B -->|uses| G[requests]
    B -->|uses| H[dotenv]
    B -->|uses| I[logging]
    
    C -->|uses| J[reportlab]
    C -->|uses| E
    
    D -.->|UI| K[User]
    
    L[auth-app.py] -->|uses| D
    L -->|uses| M[streamlit_authenticator]
    L -->|uses| N[yaml]
    L -->|uses| O[public/Logo dark.png]
    L -->|uses| P[config.yaml]
    L -->|uses| Q[usage.log]
    
    R[password_hasher.py] -->|uses| M
    
    S[api/index.py]:::api
    
    T[poc/scraping_test.py] -->|uses| U[selenium]
    T -->|uses| V[webdriver_manager]
    T -->|uses| E
    T -->|uses| W[bs4]
    T -->|uses| X[re]
    T -->|uses| Y[time]
    
    classDef api fill:#f9f,stroke:#333,stroke-width:2px;
    
    subgraph Utils
        B
        C
    end
    subgraph API
        S
    end
    subgraph POC
        T
    end
    subgraph Auth
        L
        R
    end
```

---

**Legend:**
- Main app: `app.py`
- Utility modules: `utils/`
- Auth modules: `auth-app.py`, `password_hasher.py`
- API: `api/index.py`
- Proof of concept: `poc/scraping_test.py`
- Arrows show dependency/import relationships.
- External dependencies and resources are shown as leaf nodes.

> Copy this Mermaid block into any Mermaid-compatible viewer (e.g. VSCode extension, Mermaid Live Editor, GitHub) to view the interactive graph.
