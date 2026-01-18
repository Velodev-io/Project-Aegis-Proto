#!/bin/bash

# 1. Create the Flutter project
echo "🛡️  Initializing Aegis Frontend..."
flutter create frontend

# 2. Check if creation succeeded
if [ ! -d "frontend" ]; then
    echo "❌ Error: 'flutter' command failed or not found."
    echo "   Please ensure you have Flutter installed and in your PATH."
    exit 1
fi

# 3. Inject the Prototype Code
echo "💉 Injecting source code..."
cp -R frontend_assets/lib/* frontend/lib/

# 4. Add dependencies
echo "📦 Adding dependencies..."
cd frontend
flutter pub add http

echo " "
echo "✅ Setup Complete!"
echo "🚀 To launch the app, run:"
echo "   cd frontend"
echo "   flutter run"
