#!/usr/bin/env python3
"""
Neural Network Showcase - Unified Runner
=========================================
Launch any neural network demo from a single menu.

Run: python Showcase/neural_showcase.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DEMO_CATEGORIES = {
    "Neural Networks": [
        {
            "name": "Neural Network Visualizer (Majority-3 & XOR)",
            "file": "neural_demo.py",
            "description": "Interactive visualizer for threshold logic and XOR perceptron",
            "args": ["--test"]
        },
        {
            "name": "Pattern Recognition Pipeline (SOM + Hopfield)",
            "file": "neural_pipeline_demo.py",
            "description": "Self-organizing feature maps with associative memory",
            "args": ["--test"]
        },
        {
            "name": "Kohonen Color SOM",
            "file": "kohonen_color_demo.py",
            "description": "10x10 color map self-organization (RGB space)",
            "args": ["--test"]
        }
    ],
    "Other Showcases": [
        {
            "name": "General Showcase",
            "file": "../Showcase.py",
            "description": "Main showcase with animation, terrain, and generative demos",
            "args": []
        },
        {
            "name": "Playground",
            "file": "../Playground.py",
            "description": "Interactive playground for testing .geo scripts",
            "args": []
        },
        {
            "name": "GeoStudio",
            "file": "src/GeoStudio.py",
            "description": "Studio tool for .geo script development",
            "args": []
        }
    ]
}


def print_menu():
    """Print the showcase menu."""
    print("\n" + "=" * 70)
    print("           NEURAL NETWORK SHOWCASE - Unified Runner")
    print("=" * 70)
    print()
    
    demo_index = 1
    for category, demos in DEMO_CATEGORIES.items():
        print(f"\n{category}:")
        print("-" * 70)
        for demo in demos:
            print(f"  {demo_index}. {demo['name']}")
            print(f"     {demo['description']}")
            print()
            demo_index += 1
    
    print("-" * 70)
    print("  0. Exit")
    print("=" * 70)


def run_demo(demo):
    """Run a demo by importing and executing it."""
    demo_file = demo["file"]
    demo_args = demo["args"]
    
    # Construct full path
    script_dir = os.path.dirname(__file__)
    full_path = os.path.join(script_dir, demo_file)
    
    # Check if file exists
    if not os.path.exists(full_path):
        print(f"\n❌ Error: File not found: {full_path}")
        return False
    
    print(f"\n🚀 Running: {demo['name']}")
    print(f"   File: {full_path}")
    print(f"   Args: {demo_args if demo_args else '(none)'}")
    print("-" * 70)
    
    # Add script directory to path
    script_dir = os.path.dirname(os.path.abspath(full_path))
    sys.path.insert(0, script_dir)
    
    # Save current directory
    original_dir = os.getcwd()
    original_argv = sys.argv.copy()
    
    try:
        # Change to script directory
        os.chdir(script_dir)
        
        # Set argv
        sys.argv = [demo_file] + demo_args
        
        # Execute the script
        exec_globals = {"__name__": "__main__", "__file__": full_path}
        with open(full_path, 'r', encoding='utf-8') as f:
            code = compile(f.read(), full_path, 'exec')
            exec(code, exec_globals)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        return False
    except ImportError as e:
        print(f"\n❌ Error: Import failed - {e}")
        print(f"   Make sure all dependencies are installed:")
        print(f"   pip install pygame matplotlib")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        return False
    finally:
        # Restore original directory and argv
        os.chdir(original_dir)
        sys.argv = original_argv
        # Remove script directory from path
        if script_dir in sys.path:
            sys.path.remove(script_dir)


def main():
    """Main showcase runner."""
    while True:
        print_menu()
        
        try:
            choice = input("\nEnter choice (0-{}): ".format(
                sum(len(demos) for demos in DEMO_CATEGORIES.values())
            )).strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                return
            
            # Parse choice
            choice_num = int(choice)
            total_demos = sum(len(demos) for demos in DEMO_CATEGORIES.values())
            
            if choice_num < 1 or choice_num > total_demos:
                print(f"\n❌ Invalid choice. Please enter 0-{total_demos}")
                continue
            
            # Find selected demo
            demo_index = 1
            selected_demo = None
            for category, demos in DEMO_CATEGORIES.items():
                for demo in demos:
                    if demo_index == choice_num:
                        selected_demo = demo
                        break
                    demo_index += 1
                if selected_demo:
                    break
            
            if selected_demo:
                run_demo(selected_demo)
                
                # Ask if user wants to continue
                print("\n" + "=" * 70)
                cont = input("Run another demo? (y/n): ").strip().lower()
                if cont != 'y':
                    print("\n👋 Goodbye!")
                    return
                    
        except ValueError:
            print(f"\n❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return
        except EOFError:
            print("\n\n👋 Goodbye!")
            return


if __name__ == "__main__":
    main()
