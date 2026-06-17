#!/usr/bin/env python3

from pathlib import Path
import re

# --------------------------------------------------
# Dockerfile
# --------------------------------------------------

dockerfile = Path("Dockerfile")

if dockerfile.exists():
    text = dockerfile.read_text()

    text = text.replace(
        "FROM node:20-alpine",
        "FROM node:20-bookworm"
    )

    text = text.replace(
        "npm ci --only=production",
        "npm ci --omit=dev"
    )

    dockerfile.write_text(text)
    print("✅ Dockerfile updated")
else:
    print("❌ Dockerfile not found")

# --------------------------------------------------
# prisma/schema.prisma
# --------------------------------------------------

schema = Path("prisma/schema.prisma")

if schema.exists():
    text = schema.read_text()

    generator_pattern = re.compile(
        r'generator\s+client\s*\{.*?\}',
        re.DOTALL
    )

    replacement = """generator client {
  provider      = "prisma-client-js"
  output        = "../node_modules/.prisma/client"
  binaryTargets = ["native"]
}"""

    text = generator_pattern.sub(replacement, text)

    schema.write_text(text)
    print("✅ prisma/schema.prisma updated")
else:
    print("❌ prisma/schema.prisma not found")

print("\nDone.")
print("\nNext run:")
print("docker build .")
print("or")
print("git add . && git commit -m 'Fix Prisma OpenSSL issue' && git push")
