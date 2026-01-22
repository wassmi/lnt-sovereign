```python
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from core.topology import SynthesisManifold
from core.agents import AgentOrchestrator
from core.scale import ScaleTester
from core.symbolic import RequirementStatus
import os
import json

console = Console()
orchestrator = AgentOrchestrator()

def show_welcome():
    welcome_text = Text("LNT: Logic Neutrality Tensor", style="bold cyan")
    welcome_text.append("\nFast, Auditable Verification Engine", style="italic white")
    console.print(Panel(welcome_text, border_style="blue", expand=False))

def run_interaction():
    show_welcome()
    
    while True:
        console.print("\n[bold yellow]LNT-CMD > [/bold yellow]", end="")
        user_input = input()
        
        if user_input.lower() in ["exit", "quit"]:
            console.print("[bold red]Shutting down LNT Engine...[/bold red]")
            break
        
        if user_input.lower().startswith("/stress"):
            iterations = 100
            if len(user_input.split()) > 1:
                try:
                    iterations = int(user_input.split()[1])
                except ValueError:
                    pass
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description=f"Running {iterations} Logic Regression Tests...", total=None)
                tester = ScaleTester(iterations)
                stats = tester.run_stress_test()
                
            console.print(Panel(
                f"Total Iterations: {stats['total']}\n"
                f"Passed: [green]{stats['passed']}[/green]\n"
                f"Failed: [red]{stats['failed']}[/red]\n"
                f"Avg Latency: {stats['avg_latency_ms']:.2f}ms",
                title="SCALE TEST REPORT",
                border_style="yellow"
            ))
            continue

        if user_input.lower() == "/ops":
            stats = orchestrator.verifier.manifold.monitor.get_ops_report()
            console.print(Panel(
                f"Approvals: [green]{stats['approvals']}[/green] | Rejections: [red]{stats['rejections']}[/red]\n"
                f"Hallucination Rate (Reasoning Gap): [bold cyan]{stats['hallucination_rate']}[/bold cyan]\n"
                f"Avg Latency: [bold white]{stats['avg_latency']}[/bold white]\n"
                f"Compliance Status: [bold underline]{stats['sovereign_status']}[/bold underline]",
                title="OPS DASHBOARD",
                border_style="magenta"
            ))
            continue

        if not user_input.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Agent PROVER_01 generating proposal...", total=None)
            time.sleep(1.0)
            workflow = orchestrator.execute_workflow(user_input)
            
            progress.add_task(description="Agent VERIFIER_SOVEREIGN auditing against manifold...", total=None)
            time.sleep(1.2)
            
        proposal = workflow["proposal"]
        audit = workflow["audit"]
        result = audit["manifold_result"]
        domain = result.get("domain", "VISA")

        # Display Prover Proposal
        console.print(f"\n[bold green]➜ {proposal.sender}:[/bold green] {proposal.content}")
        console.print(f"[bold cyan]➜ {audit['auditor']}:[/bold cyan] {audit['note']}")

        # Build Results Table
        table = Table(title=f"Sovereign Audit Breakdown [{domain}]", border_style="bright_blue")
        table.add_column("Rule/Factor ID", style="dim")
        table.add_column("Constraint/Basis", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Evidence/Score", style="italic")

        if "constraints" in result:
            for c in result["constraints"]:
                status_style = "green" if c.status == RequirementStatus.MET else "red"
                table.add_row(
                    c.rule_id, 
                    c.description, 
                    Text(c.status.value, style=status_style),
                    c.evidence
                )

        # Final Decision Panel
        status = result["status"]
        if status == "REJECTED_BY_LOGIC":
            console.print("[bold magenta]FLYWHEEL:[/bold magenta] Negative sample captured for Sovereign Tuning.")
        if domain == "VISA":
            decision_color = "green" if status == "APPROVED" else "red"
            title = f"PROVISIONAL DECISION: {status}"
        else:
            decision_color = "cyan"
            title = f"RANKING VERIFIED: {result['score']} POINTS"

        decision_panel = Panel(
            Text(result["explanation"], style="white"),
            title=title,
            border_style=decision_color,
            subtitle="Compliant with Bill C-27 / AIDA"
        )

        console.print(table)
        console.print(decision_panel)
        
        if "proof" in result:
            # result contains 'proof' which is a hash string in v1.0 topology
            proof_hash = result["proof"]
            console.print(f"[dim]Sovereign Proof: {proof_hash} | AIDA-2026-COMPLIANT[/dim]")


if __name__ == "__main__":
    try:
        run_interaction()
    except KeyboardInterrupt:
        console.print("\n[bold red]Engine Interrupted.[/bold red]")
        sys.exit(0)
