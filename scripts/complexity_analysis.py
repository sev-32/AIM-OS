#!/usr/bin/env python3
"""
Comprehensive Complexity Analysis for AIM-OS
Measures architectural, cognitive, and structural complexity
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import re

class ComplexityAnalyzer:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.packages_dir = self.root / "packages"
        self.metrics = {
            "cyclomatic": {},
            "cognitive": {},
            "coupling": {},
            "cohesion": {},
            "dependencies": {},
            "halstead": {},
            "maintainability": {},
            "architectural": {}
        }
    
    def cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity (decision points)"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def cognitive_complexity(self, node, depth=0) -> int:
        """Calculate cognitive complexity (how hard to understand)"""
        complexity = 0
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                # Nesting increases cognitive load
                complexity += 1 + depth
                complexity += self.cognitive_complexity(child, depth + 1)
            elif isinstance(child, ast.BoolOp):
                # Each additional condition
                complexity += len(child.values) - 1
            else:
                complexity += self.cognitive_complexity(child, depth)
        return complexity
    
    def analyze_imports(self, filepath: Path) -> Set[str]:
        """Extract all imports from a file"""
        imports = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except:
            pass
        return imports
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Comprehensive analysis of a single file"""
        metrics = {
            "functions": 0,
            "classes": 0,
            "lines": 0,
            "complexity_per_function": [],
            "cognitive_per_function": [],
            "max_nesting": 0,
            "imports": set(),
            "function_lengths": [],
            "class_methods": []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                metrics["lines"] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    cyc = self.cyclomatic_complexity(node)
                    cog = self.cognitive_complexity(node)
                    metrics["complexity_per_function"].append(cyc)
                    metrics["cognitive_per_function"].append(cog)
                    
                    # Function length
                    if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                        length = node.end_lineno - node.lineno
                        metrics["function_lengths"].append(length)
                    
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                    metrics["class_methods"].append(len(methods))
            
            metrics["imports"] = self.analyze_imports(filepath)
            
        except Exception as e:
            pass
        
        return metrics
    
    def calculate_coupling(self) -> Dict:
        """Calculate coupling between packages"""
        coupling = defaultdict(set)
        
        for package_dir in self.packages_dir.iterdir():
            if not package_dir.is_dir() or package_dir.name.startswith('.'):
                continue
            
            package_imports = set()
            for py_file in package_dir.rglob("*.py"):
                imports = self.analyze_imports(py_file)
                package_imports.update(imports)
            
            # Find internal package dependencies
            for imp in package_imports:
                if (self.packages_dir / imp).exists():
                    coupling[package_dir.name].add(imp)
        
        return dict(coupling)
    
    def calculate_dependency_depth(self, package: str, deps: Dict, visited: Set = None) -> int:
        """Calculate maximum dependency depth"""
        if visited is None:
            visited = set()
        if package in visited:
            return 0
        visited.add(package)
        
        if package not in deps or not deps[package]:
            return 0
        
        max_depth = 0
        for dep in deps[package]:
            depth = 1 + self.calculate_dependency_depth(dep, deps, visited.copy())
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def analyze_architecture(self) -> Dict:
        """Analyze architectural complexity"""
        arch = {
            "total_packages": 0,
            "total_modules": 0,
            "dependency_graph": {},
            "max_dependency_depth": 0,
            "coupling_score": 0,
            "avg_package_size": 0,
            "interface_count": 0
        }
        
        if not self.packages_dir.exists():
            return arch
        
        package_sizes = []
        for package_dir in self.packages_dir.iterdir():
            if not package_dir.is_dir() or package_dir.name.startswith('.'):
                continue
            
            arch["total_packages"] += 1
            py_files = list(package_dir.rglob("*.py"))
            arch["total_modules"] += len(py_files)
            package_sizes.append(len(py_files))
        
        # Dependency analysis
        coupling = self.calculate_coupling()
        arch["dependency_graph"] = coupling
        arch["coupling_score"] = sum(len(deps) for deps in coupling.values())
        
        # Calculate max depth
        for package in coupling:
            depth = self.calculate_dependency_depth(package, coupling)
            arch["max_dependency_depth"] = max(arch["max_dependency_depth"], depth)
        
        if package_sizes:
            arch["avg_package_size"] = sum(package_sizes) / len(package_sizes)
        
        return arch
    
    def analyze_all(self) -> Dict:
        """Run complete analysis"""
        all_metrics = {
            "cyclomatic": [],
            "cognitive": [],
            "function_lengths": [],
            "lines_per_file": [],
            "functions_per_file": [],
            "classes_per_file": [],
            "imports_per_file": [],
            "files_analyzed": 0
        }
        
        if not self.packages_dir.exists():
            print(f"Warning: {self.packages_dir} does not exist")
            return all_metrics
        
        for py_file in self.packages_dir.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'node_modules' in str(py_file):
                continue
            
            metrics = self.analyze_file(py_file)
            all_metrics["files_analyzed"] += 1
            all_metrics["cyclomatic"].extend(metrics["complexity_per_function"])
            all_metrics["cognitive"].extend(metrics["cognitive_per_function"])
            all_metrics["function_lengths"].extend(metrics["function_lengths"])
            all_metrics["lines_per_file"].append(metrics["lines"])
            all_metrics["functions_per_file"].append(metrics["functions"])
            all_metrics["classes_per_file"].append(metrics["classes"])
            all_metrics["imports_per_file"].append(len(metrics["imports"]))
        
        return all_metrics
    
    def calculate_statistics(self, values: List[float]) -> Dict:
        """Calculate statistical measures"""
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "median": 0, "p95": 0}
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        return {
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "avg": sum(values) / n,
            "median": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)] if n > 20 else sorted_vals[-1]
        }
    
    def generate_report(self) -> Dict:
        """Generate comprehensive complexity report"""
        print("🔍 Analyzing AIM-OS Complexity...")
        
        file_metrics = self.analyze_all()
        arch_metrics = self.analyze_architecture()
        
        report = {
            "summary": {
                "files_analyzed": file_metrics["files_analyzed"],
                "total_packages": arch_metrics["total_packages"],
                "total_modules": arch_metrics["total_modules"],
            },
            "cyclomatic_complexity": self.calculate_statistics(file_metrics["cyclomatic"]),
            "cognitive_complexity": self.calculate_statistics(file_metrics["cognitive"]),
            "function_length": self.calculate_statistics(file_metrics["function_lengths"]),
            "file_metrics": {
                "lines_per_file": self.calculate_statistics(file_metrics["lines_per_file"]),
                "functions_per_file": self.calculate_statistics(file_metrics["functions_per_file"]),
                "classes_per_file": self.calculate_statistics(file_metrics["classes_per_file"]),
                "imports_per_file": self.calculate_statistics(file_metrics["imports_per_file"])
            },
            "architecture": arch_metrics,
            "complexity_grade": self.grade_complexity(file_metrics, arch_metrics)
        }
        
        return report
    
    def grade_complexity(self, file_metrics, arch_metrics) -> str:
        """Assign overall complexity grade"""
        scores = []
        
        # Cyclomatic complexity (< 10 is good)
        if file_metrics["cyclomatic"]:
            avg_cyc = sum(file_metrics["cyclomatic"]) / len(file_metrics["cyclomatic"])
            scores.append("A" if avg_cyc < 5 else "B" if avg_cyc < 10 else "C")
        
        # Cognitive complexity (< 15 is good)
        if file_metrics["cognitive"]:
            avg_cog = sum(file_metrics["cognitive"]) / len(file_metrics["cognitive"])
            scores.append("A" if avg_cog < 10 else "B" if avg_cog < 20 else "C")
        
        # Coupling (< 5 dependencies per package is good)
        avg_coupling = arch_metrics["coupling_score"] / max(arch_metrics["total_packages"], 1)
        scores.append("A" if avg_coupling < 3 else "B" if avg_coupling < 5 else "C")
        
        # Depth (< 3 is good)
        scores.append("A" if arch_metrics["max_dependency_depth"] < 3 else "B" if arch_metrics["max_dependency_depth"] < 5 else "C")
        
        # Overall grade
        grade_counts = Counter(scores)
        if grade_counts["A"] >= 3:
            return "A (Excellent)"
        elif grade_counts["A"] + grade_counts["B"] >= 3:
            return "B (Good)"
        else:
            return "C (Moderate)"


def print_report(report: Dict):
    """Pretty print the complexity report"""
    print("\n" + "="*80)
    print("🎯 AIM-OS COMPLEXITY ANALYSIS REPORT")
    print("="*80)
    
    print("\n📊 SUMMARY")
    print(f"  Files Analyzed:  {report['summary']['files_analyzed']}")
    print(f"  Total Packages:  {report['summary']['total_packages']}")
    print(f"  Total Modules:   {report['summary']['total_modules']}")
    print(f"  Overall Grade:   {report['complexity_grade']}")
    
    print("\n🔢 CYCLOMATIC COMPLEXITY (Decision Points)")
    print("  (Lower is better - measures number of decision paths)")
    cyc = report['cyclomatic_complexity']
    print(f"  Average:   {cyc['avg']:.1f}")
    print(f"  Median:    {cyc['median']:.1f}")
    print(f"  Max:       {cyc['max']:.0f}")
    print(f"  95th %ile: {cyc['p95']:.0f}")
    print(f"  Grade: {'🟢 EXCELLENT' if cyc['avg'] < 5 else '🟡 GOOD' if cyc['avg'] < 10 else '🔴 HIGH'}")
    
    print("\n🧠 COGNITIVE COMPLEXITY (Mental Load)")
    print("  (Lower is better - measures how hard to understand)")
    cog = report['cognitive_complexity']
    print(f"  Average:   {cog['avg']:.1f}")
    print(f"  Median:    {cog['median']:.1f}")
    print(f"  Max:       {cog['max']:.0f}")
    print(f"  95th %ile: {cog['p95']:.0f}")
    print(f"  Grade: {'🟢 EXCELLENT' if cog['avg'] < 10 else '🟡 GOOD' if cog['avg'] < 20 else '🔴 HIGH'}")
    
    print("\n📏 FUNCTION LENGTH")
    func = report['function_length']
    print(f"  Average:   {func['avg']:.1f} lines")
    print(f"  Median:    {func['median']:.1f} lines")
    print(f"  Max:       {func['max']:.0f} lines")
    print(f"  Grade: {'🟢 EXCELLENT' if func['avg'] < 20 else '🟡 GOOD' if func['avg'] < 50 else '🔴 LONG'}")
    
    print("\n📁 FILE METRICS")
    fm = report['file_metrics']
    print(f"  Lines/File:     {fm['lines_per_file']['avg']:.1f} avg")
    print(f"  Functions/File: {fm['functions_per_file']['avg']:.1f} avg")
    print(f"  Classes/File:   {fm['classes_per_file']['avg']:.1f} avg")
    print(f"  Imports/File:   {fm['imports_per_file']['avg']:.1f} avg")
    
    print("\n🏗️ ARCHITECTURAL COMPLEXITY")
    arch = report['architecture']
    print(f"  Total Packages:        {arch['total_packages']}")
    print(f"  Avg Package Size:      {arch['avg_package_size']:.1f} modules")
    print(f"  Total Dependencies:    {arch['coupling_score']}")
    print(f"  Avg Coupling:          {arch['coupling_score'] / max(arch['total_packages'], 1):.1f} deps/package")
    print(f"  Max Dependency Depth:  {arch['max_dependency_depth']}")
    print(f"  Grade: {'🟢 LOW COUPLING' if arch['coupling_score'] < 15 else '🟡 MODERATE' if arch['coupling_score'] < 30 else '🔴 HIGH'}")
    
    print("\n🔗 DEPENDENCY GRAPH")
    for package, deps in arch['dependency_graph'].items():
        if deps:
            print(f"  {package} → {', '.join(sorted(deps))}")
    
    print("\n" + "="*80)
    print("📈 INTERPRETATION")
    print("="*80)
    
    cyc_avg = report['cyclomatic_complexity']['avg']
    cog_avg = report['cognitive_complexity']['avg']
    coupling = arch['coupling_score'] / max(arch['total_packages'], 1)
    
    if cyc_avg < 5 and cog_avg < 10 and coupling < 3:
        print("✨ EXCEPTIONAL: Code is simple, readable, and loosely coupled.")
        print("   This is production-ready, maintainable architecture.")
    elif cyc_avg < 10 and cog_avg < 20 and coupling < 5:
        print("✅ EXCELLENT: Code is well-structured with good separation of concerns.")
        print("   Easy to maintain and extend.")
    elif cyc_avg < 15 and cog_avg < 30 and coupling < 8:
        print("👍 GOOD: Code is reasonable but could benefit from refactoring.")
        print("   Some functions might be doing too much.")
    else:
        print("⚠️  COMPLEX: Consider refactoring to reduce complexity.")
        print("   Break down large functions and reduce coupling.")
    
    print("\n🎓 BENCHMARKS (Industry Standards)")
    print("  Cyclomatic:  1-4 (Simple), 5-10 (Complex), 10+ (Very Complex)")
    print("  Cognitive:   1-10 (Low), 11-20 (Moderate), 20+ (High)")
    print("  Coupling:    <3 (Loose), 3-5 (Moderate), 5+ (Tight)")
    print("  Depth:       <3 (Shallow), 3-5 (Moderate), 5+ (Deep)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    analyzer = ComplexityAnalyzer()
    report = analyzer.generate_report()
    print_report(report)
    
    # Save to file
    output_file = Path("analysis/COMPLEXITY_METRICS.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n💾 Detailed metrics saved to: {output_file}")

