# Generated migration for survival game models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GameState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scenario_name", models.CharField(default="Nuclear Winter", max_length=200)),
                ("scenario_data", models.JSONField(default=dict)),
                ("total_players", models.IntegerField(default=0)),
                ("bunker_capacity", models.IntegerField(default=0)),
                ("round_number", models.IntegerField(default=0)),
                (
                    "attribute_order",
                    models.JSONField(
                        default=list,
                        help_text="Ordered list of attribute names; one is revealed per round.",
                    ),
                ),
                ("survivors", models.JSONField(default=list)),
                ("total_points", models.IntegerField(default=0)),
                (
                    "outcome",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("success", "Success"),
                            ("failure", "Failure"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "player_id",
                    models.CharField(
                        db_index=True,
                        help_text="UUID assigned on join; shared with client as their identity token.",
                        max_length=36,
                        unique=True,
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="players",
                        to="game.gamestate",
                    ),
                ),
                (
                    "attributes",
                    models.JSONField(
                        default=dict,
                        help_text="Complete attribute dict. Keep hidden until revealed by round logic.",
                    ),
                ),
                (
                    "revealed_attrs",
                    models.JSONField(
                        default=dict,
                        help_text="Attribute key/value pairs revealed so far.",
                    ),
                ),
                ("votes_received", models.IntegerField(default=0)),
                (
                    "vote_log",
                    models.JSONField(
                        default=list,
                        help_text="List of {round, voters} dicts recording who voted for this player.",
                    ),
                ),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
