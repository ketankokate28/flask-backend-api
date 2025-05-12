class Recipient(db.Model):
    __tablename__ = 'recipients'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(20))
    channels = Column(String(50), nullable=False)  # comma-separated, e.g. 'EMAIL,SMS,VOICE'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # backref from CallTreeEntry and NotificationRecipient
    call_tree_entries = relationship('CallTreeEntry', back_populates='recipient', cascade='all, delete-orphan')
    notifications = relationship('NotificationRecipient', back_populates='recipient', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Recipient {self.id} {self.name}>"