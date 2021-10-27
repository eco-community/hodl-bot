from tortoise import fields
from tortoise.models import Model

from app.validators import PositiveValueValidator
from app.constants import DEFAULT_EPOCH_APY, DEFAULT_PORTFOLIO_PERCENTAGE


class User(Model):
    """User table"""

    id = fields.BigIntField(pk=True)  # same as https://discordpy.readthedocs.io/en/latest/api.html#discord.User.id
    balance = fields.data.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        validators=[PositiveValueValidator()],
    )
    is_staking = fields.BooleanField(default=False)  # is user participating in staking or not
    staking_started_date = fields.data.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id}"


class Epoch(Model):
    """Stacking Epoch table"""

    id = fields.IntField(pk=True)
    start_datetime = fields.data.DatetimeField()
    end_datetime = fields.data.DatetimeField()
    # APY per epoch in % (aka 0.025 means 2.5%)
    apy = fields.data.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=DEFAULT_EPOCH_APY,
        validators=[PositiveValueValidator()],
    )
    # part of the User.balance which will be staked (aka 0.2 means 20% of user's points wil be stakes)
    portfolio_percentage = fields.data.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=DEFAULT_PORTFOLIO_PERCENTAGE,
        validators=[PositiveValueValidator()],
    )
    users = fields.ManyToManyField("app.User", related_name="epochs", through="user_epoch")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    user_epochs: fields.ReverseRelation["UserEpoch"]

    def __str__(self):
        return f"Epoch №{self.id}"


class UserEpoch(Model):
    """Many to many relationship between user and epoch"""

    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("app.User", related_name="user_epochs")
    epoch = fields.ForeignKeyField("app.Epoch", related_name="user_epochs")
    # this balance will be used to determine APY per epoch (epoch_lowest_balance * apy)
    epoch_lowest_balance = fields.data.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        validators=[PositiveValueValidator()],
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    epochs: fields.ReverseRelation["Epoch"]

    def __str__(self):
        return f"UserEpoch №{self.id}"

    class Meta:
        table = "user_epoch"
