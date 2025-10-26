#!/bin/bash
# Script to restart Next.js dev server with cache clearing

echo "🧹 Clearing Next.js cache..."
rm -rf .next

echo "📦 Installing dependencies (if needed)..."
npm install

echo "🚀 Starting dev server..."
npm run dev
